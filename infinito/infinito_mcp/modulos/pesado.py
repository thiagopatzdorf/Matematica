"""Módulo pesado: trabalho que custa dinheiro de verdade (VM spot) e por isso passa pelo ledger.

O contrato é o do ledger `GeminiUso` da loja: **reserva antes, confirma depois, cancela se não
rodou**. Nada aqui chama a nuvem por conta própria: quem executa é um `Executor` injetado.

Estado desta entrega (2026-10-03): o único executor existente é `ExecutorNenhum`, que **recusa**.
Ligar uma VM é gasto e decisão do Thiago; até ele liberar, `pesado(confirmar=true)` reserva,
descobre que não há executor, cancela a reserva e diz isso — nunca finge que rodou. O executor
real (VM spot `lean-build2` pela service account própria, com teto de horas) é a próxima peça
e entra por `INF_EXECUTOR`.
"""
from __future__ import annotations

from typing import Protocol

from ..creditos import ErroCreditos

NOME = "pesado"
# tipo -> (descrição, horas máximas por pedido). Allowlist: o agente não manda comando, escolhe um tipo.
TIPOS = {
    "lake_build": ("`lake build` do repo (alvo padrão ou um alvo nomeado)", 3.0),
    "busca": ("busca de código de cobertura (scripts/search) numa célula", 6.0),
    "verificar_grande": ("verificador oficial em espaço grande (q^n > 1e9)", 2.0),
}


class Executor(Protocol):
    def iniciar(self, tipo: str, parametros: dict, horas: float, quem: str) -> dict: ...


class ExecutorNenhum:
    def iniciar(self, tipo, parametros, horas, quem):
        raise ErroCreditos("nenhum executor de VM ligado neste deploy: nada foi gasto e nada rodou")


def registrar(ctx, executor: Executor | None = None) -> None:
    tool, creditos = ctx.tool, ctx.creditos
    executor = executor or ExecutorNenhum()
    tarifa = float(ctx.env.get("INF_TARIFA_HORA_USD", "0.60"))   # e2-highmem-8, margem para cima

    @tool
    def pesado_tipos() -> dict:
        """Tipos de trabalho pesado, o teto de horas de cada um e a tarifa por hora (US$)."""
        return {"ok": True, "tarifa_hora_usd": tarifa,
                "tipos": {k: {"descricao": d, "horas_max": h, "custo_max_usd": round(h * tarifa, 2)} for k, (d, h) in TIPOS.items()}}

    @tool
    def pesado(tipo: str, horas: float, parametros: dict | None = None, confirmar: bool = False) -> dict:
        """Pede trabalho pesado. Sem confirmar=true só mostra custo estimado e saldo (seco). Com confirmar=true
        reserva o custo no seu crédito, roda e confirma o gasto real; se não puder rodar, a reserva é desfeita."""
        if tipo not in TIPOS:
            return {"ok": False, "erro": f"tipo inválido; use um de: {', '.join(TIPOS)}"}
        descricao, max_h = TIPOS[tipo]
        if not 0 < horas <= max_h:
            return {"ok": False, "erro": f"horas tem de estar em (0, {max_h}] para {tipo}"}
        custo = round(horas * tarifa, 4)
        saldo = creditos.saldo(ctx.quem())
        if not confirmar:
            return {"ok": True, "seco": True, "tipo": tipo, "custo_estimado_usd": custo, "saldo": saldo,
                    "cabe": saldo["disponivel_usd"] is None or custo <= saldo["disponivel_usd"]}
        reserva = creditos.reservar(ctx.quem(), f"pesado:{tipo}", custo)
        try:
            job = executor.iniciar(tipo, parametros or {}, horas, ctx.quem())
        except Exception as e:  # noqa: BLE001 - não rodou, não cobra
            creditos.cancelar(ctx.quem(), reserva)
            return {"ok": False, "erro": str(e) if isinstance(e, ErroCreditos) else f"executor falhou ({type(e).__name__}); reserva desfeita"}
        # O custo REAL é confirmado quando o job termina (executor real); aqui fica a reserva aberta.
        return {"ok": True, "seco": False, "reserva": reserva, "job": job, "reservado_usd": custo}
