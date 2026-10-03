"""Módulo pesado: trabalho que custa dinheiro de verdade (a VM `lean-build2`) e por isso passa pelo ledger.

Contrato (o do ledger `GeminiUso` da loja): **reserva antes, liquida depois, cancela se não rodou**.

1. `pesado(confirmar=true)` reserva `horas × tarifa` (o pior caso), liga a VM com o job e grava `jobs/<id>.json`;
2. `pesado_status` (de qualquer pessoa, a qualquer hora) lê a VM: terminou → cobra o **tempo real** de máquina ligada
   (nunca mais que o pedido); passou do prazo → desliga e cobra o pedido inteiro; nunca chegou a ligar → cancela;
3. quem pede um job novo liquida antes os que já acabaram, então a reserva de um job terminado não trava ninguém.

Sem `INF_EXECUTOR=vm` não há executor: o pedido reserva, descobre, cancela e diz isso. Nunca finge que rodou.
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Protocol

from ..creditos import ErroCreditos

NOME = "pesado"
# tipo -> (descrição, horas máximas por pedido). Allowlist: o agente escolhe um tipo, nunca manda comando.
TIPOS = {
    "lake_build": ("`lake build` do repo na VM (alvo opcional, ex.: CoveringLean.Syn_K1137); o alvo padrão leva ~5 min", 3.0),
    "verificar_grande": ("verificador oficial em C num código de data/codes (parâmetro: arquivo), para q^n grande", 2.0),
}
JOBS = "jobs/"
PRAZO_EXTRA_S = 120


class Executor(Protocol):
    def iniciar(self, tipo: str, parametros: dict, horas: float, quem: str, job_id: str = "") -> dict: ...
    def status(self, job_id: str) -> dict: ...
    def parar(self) -> None: ...
    def liberar(self) -> None: ...


class ExecutorNenhum:
    def iniciar(self, tipo, parametros, horas, quem, job_id=""):
        raise ErroCreditos("nenhum executor de VM ligado neste deploy: nada foi gasto e nada rodou")

    def status(self, job_id):
        return {}

    def parar(self):
        pass

    def liberar(self):
        pass


def registrar(ctx, executor: Executor | None = None, agora=time.time) -> None:
    tool, creditos, estado = ctx.tool, ctx.creditos, ctx.estado
    if executor is None:
        env = ctx.env
        if env.get("INF_EXECUTOR") == "vm" and env.get("INF_GCP_PROJETO"):
            from ..executor_vm import ExecutorVM
            executor = ExecutorVM(env["INF_GCP_PROJETO"], env.get("INF_VM_ZONA", "southamerica-east1-a"),
                                  env.get("INF_VM_NOME", "lean-build2"))
        else:
            executor = ExecutorNenhum()
    tarifa = float(ctx.env.get("INF_TARIFA_HORA_USD", "0.60"))   # e2-highmem-8 sob demanda, margem para cima

    def _ler(job_id: str) -> dict | None:
        b = estado.ler(f"{JOBS}{job_id}.json")
        return json.loads(b) if b else None

    def _gravar(job: dict) -> None:
        estado.por(f"{JOBS}{job['id']}.json", json.dumps(job, ensure_ascii=False).encode(), "application/json", publico=False)

    def _abertos() -> list[dict]:
        jobs = [json.loads(estado.ler(n)) for n in estado.listar(JOBS)]
        return [j for j in jobs if j["estado"] in ("pedido", "rodando")]

    def _liquidar(job: dict) -> dict:
        """Olha a VM e, se o job acabou, cobra. Idempotente: job já liquidado volta como está."""
        if job["estado"] not in ("pedido", "rodando"):
            return job
        st = executor.status(job["id"])
        t0, agora_ = job["iniciado"], agora()
        terminou = st.get("estado") == "concluido" or (st.get("vm") == "TERMINATED" and (st.get("inicio_vm") or 0) >= t0 - 30)
        nunca_ligou = st.get("vm") == "TERMINATED" and (st.get("inicio_vm") or 0) < t0 - 30
        if terminou:
            # Máquina desligada: vale o carimbo de parada da própria VM (é quando a cobrança acaba). Ainda ligada: o fim
            # do job + 30 s de desligamento.
            fim = (st.get("fim_vm") if st.get("vm") == "TERMINATED" else None) or ((st["fim"] + 30) if st.get("fim") else agora_)
            horas = min(max(fim - (st.get("inicio_vm") or t0), 0) / 3600, job["horas"])
            custo = round(max(horas * tarifa, 0.01), 4)                  # piso de 1 centavo: ligar a máquina nunca é grátis
            creditos.confirmar(job["quem"], job["reserva"], custo)
            job.update(estado="liquidado", custo_usd=custo, horas_reais=round(horas, 4), codigo=st.get("codigo"),
                       saida=st.get("saida", ""), liquidado=agora_)
            executor.liberar()
        elif nunca_ligou:
            creditos.cancelar(job["quem"], job["reserva"])
            job.update(estado="nao_rodou", custo_usd=0.0, liquidado=agora_)
        elif agora_ - t0 > job["horas"] * 3600 + PRAZO_EXTRA_S:          # estourou: desliga e cobra o pedido inteiro
            executor.parar()
            custo = round(job["horas"] * tarifa, 4)
            creditos.confirmar(job["quem"], job["reserva"], custo)
            job.update(estado="liquidado", custo_usd=custo, horas_reais=job["horas"], codigo=None,
                       saida="passou do prazo: a VM foi desligada e o tempo pedido foi cobrado", liquidado=agora_)
            executor.liberar()
        else:
            job["estado"] = "rodando"
        _gravar(job)
        return job

    @tool
    def pesado_tipos() -> dict:
        """Tipos de trabalho pesado, o teto de horas de cada um e a tarifa por hora (US$)."""
        return {"ok": True, "tarifa_hora_usd": tarifa,
                "tipos": {k: {"descricao": d, "horas_max": h, "custo_max_usd": round(h * tarifa, 2)} for k, (d, h) in TIPOS.items()}}

    @tool
    def pesado(tipo: str, horas: float, parametros: dict | None = None, confirmar: bool = False) -> dict:
        """Pede trabalho pesado na VM. Sem confirmar=true só mostra custo máximo e saldo (seco). Com confirmar=true
        reserva o custo máximo no seu crédito, liga a VM e devolve o `job`; acompanhe com `pesado_status`. Ao terminar
        é cobrado só o tempo real de máquina ligada. Um job por vez: se a VM está ocupada, recusa e não cobra."""
        if tipo not in TIPOS:
            return {"ok": False, "erro": f"tipo inválido; use um de: {', '.join(TIPOS)}"}
        descricao, max_h = TIPOS[tipo]
        if not 0 < horas <= max_h:
            return {"ok": False, "erro": f"horas tem de estar em (0, {max_h}] para {tipo}"}
        custo = round(horas * tarifa, 4)
        for j in _abertos():                                            # job que acabou não pode trancar a reserva dos outros
            _liquidar(j)
        saldo = creditos.saldo(ctx.quem())
        if not confirmar:
            return {"ok": True, "seco": True, "tipo": tipo, "custo_maximo_usd": custo, "saldo": saldo,
                    "cabe": saldo["disponivel_usd"] is None or custo <= saldo["disponivel_usd"],
                    "vm_ocupada": bool(_abertos())}
        reserva = creditos.reservar(ctx.quem(), f"pesado:{tipo}", custo)
        job_id = uuid.uuid4().hex[:12]
        try:
            info = executor.iniciar(tipo, parametros or {}, horas, ctx.quem(), job_id)
        except Exception as e:  # noqa: BLE001 - não rodou, não cobra
            creditos.cancelar(ctx.quem(), reserva)
            return {"ok": False, "erro": str(e) if isinstance(e, ErroCreditos) else f"executor falhou ({type(e).__name__}); reserva desfeita"}
        _gravar({"id": job_id, "quem": ctx.quem(), "tipo": tipo, "params": parametros or {}, "horas": horas,
                 "reserva": reserva, "reservado_usd": custo, "estado": "pedido", "iniciado": agora(), "info": info})
        return {"ok": True, "seco": False, "job": job_id, "reservado_usd": custo, "vm": info,
                "proximo": "pesado_status(job) para ver o andamento; o custo real é cobrado quando terminar"}

    @tool
    def pesado_status(job: str = "") -> dict:
        """Andamento dos seus jobs (ou de um `job`). Se o job terminou, liquida: cobra o tempo real e mostra o
        código de saída e o fim do log. Se passou do prazo, desliga a VM. Administrador vê o de qualquer pessoa."""
        if job:
            j = _ler(job)
            if not j or (j["quem"] != ctx.quem() and not creditos.e_admin(ctx.quem())):
                return {"ok": False, "erro": "job não encontrado"}
            jobs = [j]
        else:
            jobs = [json.loads(estado.ler(n)) for n in estado.listar(JOBS)]
            jobs = [j for j in jobs if j["quem"] == ctx.quem() or creditos.e_admin(ctx.quem())][-10:]
        saida = []
        for j in jobs:
            j = _liquidar(j)
            saida.append({k: j.get(k) for k in ("id", "quem", "tipo", "estado", "horas", "reservado_usd", "custo_usd",
                                               "horas_reais", "codigo", "saida") if k in j})
        return {"ok": True, "jobs": saida}
