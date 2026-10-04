"""Módulo Gemini: chamada paga ao modelo, sempre pelo ledger de créditos.

Mesmo contrato do ledger `GeminiUso` da loja: **reserva o pior caso antes, confirma o custo real
depois, cancela se a chamada falhou**. O custo do pior caso é entrada estimada + `max_saida` tokens
de saída, então nenhuma chamada pode passar do que a pessoa tem disponível.

Dois caminhos, escolhidos pelo ambiente:

* **Vertex AI (padrão no Cloud Run, `INF_GEMINI_BACKEND=vertex`)**: o token da service account do serviço, pelo
  metadata server. Sem chave em lugar nenhum e sem crédito pré-pago: cobra na fatura do projeto GCP. Medido em
  2026-10-03: `gemini-3.8-flash` responde em `locations/global` (nas regiões `southamerica-east1`/`us-central1` o
  3.8 dá 404). A SA precisa de `roles/aiplatform.user`.
* **Chave de API (`GEMINI_API_KEY`)**: a do AI Studio, que é pré-paga. A do cofre estava sem crédito (HTTP 402).

Sem nenhum dos dois, a tool recusa e desfaz a reserva. Os preços são **US$ por milhão de tokens** e moram em
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
# US$/milhão de tokens, de https://ai.google.dev/gemini-api/docs/pricing lida em 2026-10-03 (via resumo automático da
# página: reconfira antes de aumentar crédito). Para o 3.8-flash vale a tarifa DE 2027 (a de 2026 é metade): o teto
# nunca subestima. Pro usa a faixa de prompt > 200k. O gemini-2.5-* foi aposentado pela API (404 medido em 2026-10-03).
PRECOS_PADRAO = {"gemini-3.8-flash": [1.50, 7.50], "gemini-3.5-flash": [1.50, 9.00], "gemini-3.1-pro-preview": [4.00, 18.00]}
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
        return {"texto": texto, "entrada": u.get("promptTokenCount", 0), "fim": _fim(d),
                "saida": u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)}
    return chamar


METADATA = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
VERTEX = "https://aiplatform.googleapis.com/v1/projects/{projeto}/locations/global/publishers/google/models/{modelo}:generateContent"


def token_metadata() -> str:
    req = urllib.request.Request(METADATA, headers={"Metadata-Flavor": "Google"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["access_token"]


def chamar_vertex(projeto: str, token: Callable[[], str] = token_metadata, post=None) -> Chamada:
    """Vertex AI com o token da SA do serviço. `post(url, corpo, cabecalhos) -> dict` é injetável nos testes."""
    def _post(url, corpo, cab):
        req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST", headers=cab)
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())

    enviar = post or _post

    def chamar(modelo: str, prompt: str, max_saida: int) -> dict:
        d = enviar(VERTEX.format(projeto=projeto, modelo=modelo),
                   {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_saida}},
                   {"Content-Type": "application/json", "Authorization": "Bearer " + token()})
        u = d.get("usageMetadata", {})
        texto = "".join(p.get("text", "") for c in d.get("candidates", [])[:1]
                        for p in c.get("content", {}).get("parts", []))
        return {"texto": texto, "entrada": u.get("promptTokenCount", 0), "fim": _fim(d),
                "saida": u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)}
    return chamar


def _fim(d: dict) -> str:
    return (d.get("candidates") or [{}])[0].get("finishReason", "")


def custo(precos: list[float], entrada: int, saida: int) -> float:
    return (entrada * precos[0] + saida * precos[1]) / 1e6


def registrar(ctx, chamada: Chamada | None = None) -> None:
    tool, creditos = ctx.tool, ctx.creditos
    precos = json.loads(ctx.env["INF_GEMINI_PRECOS"]) if ctx.env.get("INF_GEMINI_PRECOS") else PRECOS_PADRAO
    padrao = ctx.env.get("INF_GEMINI_MODELO", "gemini-3.8-flash")
    chave = ctx.env.get("GEMINI_API_KEY", "")
    projeto = ctx.env.get("INF_GCP_PROJETO", "")
    if chamada is None:
        if ctx.env.get("INF_GEMINI_BACKEND") == "vertex" and projeto:
            chamada = chamar_vertex(projeto)
        elif chave:
            chamada = chamar_api(chave)

    @tool
    def gemini(prompt: str, modelo: str = "", max_saida: int = 2048, confirmar: bool = False) -> dict:
        """Pergunta ao Gemini, descontando do seu crédito. Sem confirmar=true só mostra o custo máximo e o saldo.
        Com confirmar=true reserva o pior caso, chama e cobra o custo real (tokens medidos pela API).
        ATENÇÃO: o "pensamento" do modelo conta dentro de max_saida; se `fim` vier MAX_TOKENS a resposta saiu cortada,
        aumente max_saida (até 8192)."""
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
            return {"ok": False, "erro": "nenhum backend do Gemini configurado (Vertex ou GEMINI_API_KEY): nada foi gasto"}
        try:
            r = chamada(modelo, prompt, max_saida)
        except Exception as e:  # noqa: BLE001 - não respondeu, não cobra
            creditos.cancelar(ctx.quem(), reserva)
            http = getattr(e, "code", "")
            return {"ok": False, "erro": f"Gemini não respondeu ({type(e).__name__} {http}); reserva desfeita".replace("  ", " ")}
        real = round(custo(precos[modelo], r["entrada"], r["saida"]), 6)   # o real, mesmo se passar da estimativa
        creditos.confirmar(ctx.quem(), reserva, real)
        return {"ok": True, "seco": False, "modelo": modelo, "texto": r["texto"], "tokens_entrada": r["entrada"],
                "tokens_saida": r["saida"], "fim": r.get("fim", ""), "custo_usd": real, "saldo": creditos.saldo(ctx.quem())}
