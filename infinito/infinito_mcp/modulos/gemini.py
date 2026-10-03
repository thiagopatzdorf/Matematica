"""Módulo Gemini: chamada paga ao modelo, sempre pelo ledger de créditos.

Mesmo contrato do ledger `GeminiUso` da loja: **reserva o pior caso antes, confirma o custo real
depois, cancela se a chamada falhou**. O custo do pior caso é entrada estimada + `max_saida` tokens
de saída, então nenhuma chamada pode passar do que a pessoa tem disponível.

A chave (`GEMINI_API_KEY`) vem do ambiente do serviço (Secret Manager no deploy) e nunca é devolvida.
Sem chave, a tool recusa e desfaz a reserva. Os preços são **US$ por milhão de tokens** e moram em
`INF_GEMINI_PRECOS` (JSON `{"modelo": [entrada, saida]}`): conferir contra a tabela oficial antes de
liberar para mais gente, porque preço muda e o teto só vale se o preço estiver certo.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Callable

from ..creditos import ErroCreditos

NOME = "gemini"
API = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
PRECOS_PADRAO = {"gemini-2.5-flash": [0.30, 2.50], "gemini-2.5-pro": [1.25, 10.00]}  # NÃO conferido em 2026-10-03
MAX_SAIDA = 8192

Chamada = Callable[[str, str, int], dict]


def chamar_api(chave: str) -> Chamada:
    def chamar(modelo: str, prompt: str, max_saida: int) -> dict:
        corpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"maxOutputTokens": max_saida}}).encode()
        req = urllib.request.Request(API.format(modelo=modelo), data=corpo, method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": chave})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        u = d.get("usageMetadata", {})
        texto = "".join(p.get("text", "") for c in d.get("candidates", [])[:1]
                        for p in c.get("content", {}).get("parts", []))
        return {"texto": texto, "entrada": u.get("promptTokenCount", 0),
                "saida": u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)}
    return chamar


def custo(precos: list[float], entrada: int, saida: int) -> float:
    return (entrada * precos[0] + saida * precos[1]) / 1e6


def registrar(ctx, chamada: Chamada | None = None) -> None:
    tool, creditos = ctx.tool, ctx.creditos
    precos = json.loads(ctx.env["INF_GEMINI_PRECOS"]) if ctx.env.get("INF_GEMINI_PRECOS") else PRECOS_PADRAO
    padrao = ctx.env.get("INF_GEMINI_MODELO", "gemini-2.5-flash")
    chave = ctx.env.get("GEMINI_API_KEY", "")
    chamada = chamada or (chamar_api(chave) if chave else None)

    @tool
    def gemini(prompt: str, modelo: str = "", max_saida: int = 1024, confirmar: bool = False) -> dict:
        """Pergunta ao Gemini, descontando do seu crédito. Sem confirmar=true só mostra o custo máximo e o saldo.
        Com confirmar=true reserva o pior caso, chama e cobra o custo real (tokens medidos pela API)."""
        modelo = modelo or padrao
        if modelo not in precos:
            return {"ok": False, "erro": f"modelo sem preço cadastrado; use um de: {', '.join(precos)}"}
        if not prompt.strip():
            return {"ok": False, "erro": "prompt vazio"}
        max_saida = max(1, min(max_saida, MAX_SAIDA))
        entrada_est = len(prompt) // 3 + 1                      # pessimista: ~3 caracteres por token
        pior = round(custo(precos[modelo], entrada_est, max_saida), 6)
        saldo = creditos.saldo(ctx.quem())
        if not confirmar:
            return {"ok": True, "seco": True, "modelo": modelo, "custo_maximo_usd": pior, "saldo": saldo,
                    "cabe": saldo["disponivel_usd"] is None or pior <= saldo["disponivel_usd"]}
        reserva = creditos.reservar(ctx.quem(), f"gemini:{modelo}", pior)
        if chamada is None:
            creditos.cancelar(ctx.quem(), reserva)
            return {"ok": False, "erro": "GEMINI_API_KEY não configurada neste deploy: nada foi gasto"}
        try:
            r = chamada(modelo, prompt, max_saida)
        except Exception as e:  # noqa: BLE001 - não respondeu, não cobra
            creditos.cancelar(ctx.quem(), reserva)
            return {"ok": False, "erro": f"Gemini não respondeu ({type(e).__name__}); reserva desfeita"}
        real = round(custo(precos[modelo], r["entrada"], r["saida"]), 6)   # o real, mesmo se passar da estimativa
        creditos.confirmar(ctx.quem(), reserva, real)
        return {"ok": True, "seco": False, "modelo": modelo, "texto": r["texto"], "tokens_entrada": r["entrada"],
                "tokens_saida": r["saida"], "custo_usd": real, "saldo": creditos.saldo(ctx.quem())}
