"""Módulo pesado: trabalho que custa dinheiro de verdade (VMs spot efêmeras) e por isso passa pelo ledger.

Contrato (o do ledger `GeminiUso` da loja): **reserva antes, liquida depois, cancela se não rodou, nunca finge**.

1. `pesado(..., paralelo=N, confirmar=true)` reserva `N × horas × tarifa(máquina)` — o pior caso do lote INTEIRO —,
   grava `jobs/<id>.json` e só então cria as N VMs (executor_lote.py). Se uma não sobe, as outras são apagadas e a
   reserva volta;
2. `pesado_status` (de qualquer pessoa, a qualquer hora) lê cada shard: terminou → cobra o **tempo real** daquela VM
   e a apaga; sumiu (preempção spot, ou o Compute apagou no prazo) → cobra até agora, limitado ao pedido; passou do
   prazo → apaga e cobra o pedido inteiro. O job liquida quando todos os shards fecharam;
3. toda chamada de `pesado`/`pesado_status` antes liquida os jobs abertos e **varre órfãs**: VM com o rótulo do
   Infinito cujo job já fechou (ou não existe) é apagada. Junto com o `maxRunDuration` com DELETE de cada VM, é o
   que garante que nenhuma máquina fica viva depois do prazo.

Tipos são allowlist: o agente escolhe um tipo e parâmetros validados; `script` roda `pesado/jobs/<nome>.sh` de um
commit que a VM confere estar na `main`, com `SHARD_INDEX`/`SHARD_TOTAL` no ambiente. Comando livre não existe.
Sem `INF_EXECUTOR=lote` não há executor: o pedido reserva, descobre, cancela e diz isso.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Protocol

from ..creditos import ErroCreditos
from ..executor_lote import MAQUINAS, tarifa_hora

NOME = "pesado"
# tipo -> (descrição, horas máximas por shard).
TIPOS = {
    "lake_build": ("`lake build` do repo (alvo opcional, ex.: CoveringLean.Syn_K1137); o alvo padrão leva ~5 min", 3.0),
    "verificar_grande": ("verificador oficial em C num código de data/codes (parâmetro: arquivo), para q^n grande", 2.0),
    "script": ("roda pesado/jobs/<nome>.sh de um commit que já está na main; cada shard recebe SHARD_INDEX/SHARD_TOTAL "
               "e grava arquivos em $SAIDA (sobem para o bucket)", 6.0),
}
JOBS = "jobs/"
PRAZO_EXTRA_S = 120
NOME_SCRIPT = re.compile(r"[a-z0-9][a-z0-9_-]{0,39}")
COMMIT = re.compile(r"[0-9a-f]{7,40}")
ABERTOS = ("subindo", "pedido", "rodando")


class Executor(Protocol):
    def iniciar(self, job_id: str, tipo: str, parametros: dict, horas: float, quem: str, paralelo: int,
                maquina: str) -> dict: ...
    def status(self, job_id: str, total: int) -> list[dict]: ...
    def apagar(self, job_id: str, total: int) -> None: ...
    def apagar_nome(self, nome: str) -> None: ...
    def listar(self) -> list[dict]: ...


class ExecutorNenhum:
    def iniciar(self, *a, **k):
        raise ErroCreditos("nenhum executor de VM ligado neste deploy: nada foi gasto e nada rodou")

    def status(self, job_id, total):
        return [{"existe": False} for _ in range(total)]

    def apagar(self, job_id, total):
        pass

    def apagar_nome(self, nome):
        pass

    def listar(self):
        return []


def _executor_do_ambiente(env: dict) -> Executor:
    if env.get("INF_EXECUTOR") != "lote" or not env.get("INF_GCP_PROJETO"):
        return ExecutorNenhum()
    from ..executor_lote import ExecutorLote, assinador_da_sa
    assinar = None if env.get("INF_PESADO_ASSINAR") == "0" else assinador_da_sa(env.get("INF_BUCKET_ESTADO", ""))
    return ExecutorLote(env["INF_GCP_PROJETO"], env.get("INF_VM_ZONA", "southamerica-east1-a"),
                        env.get("INF_PESADO_IMAGEM", "bkp-lean-build2-20261006"), assinador=assinar,
                        disco_gb=int(env.get("INF_PESADO_DISCO_GB", "100")),
                        tipo_disco=env.get("INF_PESADO_TIPO_DISCO", "pd-balanced"))


def registrar(ctx, executor: Executor | None = None, agora=time.time) -> None:
    tool, creditos, estado, env = ctx.tool, ctx.creditos, ctx.estado, ctx.env
    executor = executor or _executor_do_ambiente(env)
    paralelo_max = int(env.get("INF_PESADO_PARALELO_MAX", "8"))
    maquina_padrao = env.get("INF_PESADO_MAQUINA", "e2-highmem-8")
    margem = float(env.get("INF_PESADO_MARGEM", "1.2"))
    disco_gb, tipo_disco = int(env.get("INF_PESADO_DISCO_GB", "100")), env.get("INF_PESADO_TIPO_DISCO", "pd-balanced")
    sobrepor = json.loads(env.get("INF_PESADO_TARIFAS", "{}"))       # {"máquina": US$/h} se o preço mudar
    pasta_jobs = Path(env.get("INF_REPO", "")) / "pesado" / "jobs" if env.get("INF_REPO") else None

    def tarifa(maquina: str) -> float:
        return float(sobrepor[maquina]) if maquina in sobrepor else tarifa_hora(maquina, disco_gb, tipo_disco, margem)

    def scripts() -> list[str] | None:
        """Os scripts da allowlist que este servidor conhece (a imagem copia a pasta). None = não sabe: a VM decide."""
        if not pasta_jobs or not pasta_jobs.is_dir():
            return None
        return sorted(p.stem for p in pasta_jobs.glob("*.sh") if NOME_SCRIPT.fullmatch(p.stem))

    def _ler(job_id: str) -> dict | None:
        b = estado.ler(f"{JOBS}{job_id}.json")
        return json.loads(b) if b else None

    def _gravar(job: dict) -> None:
        estado.por(f"{JOBS}{job['id']}.json", json.dumps(job, ensure_ascii=False).encode(), "application/json", publico=False)

    def _todos() -> list[dict]:
        return [json.loads(estado.ler(n)) for n in estado.listar(JOBS) if n.endswith(".json") and n.count("/") == 1]

    def _fechar_shard(job: dict, sh: dict, horas: float, codigo, saida: str, motivo: str) -> None:
        horas = min(max(horas, 0.0), job["horas"])
        sh.update(estado="fechado", horas_reais=round(horas, 4), custo_usd=round(horas * job["tarifa_hora_usd"], 4),
                  codigo=codigo, saida=saida[-3000:], motivo=motivo)
        estado.por(f"{JOBS}{job['id']}/shard-{sh['i']}.txt", saida.encode(), "text/plain", publico=False)

    def _liquidar(job: dict) -> dict:
        """Olha cada shard e cobra o que fechou. Idempotente: shard ou job já fechado volta como está."""
        if job["estado"] not in ABERTOS:
            return job
        agora_, t0 = agora(), job["iniciado"]
        estourou = agora_ - t0 > job["horas"] * 3600 + PRAZO_EXTRA_S
        for sh, st in zip(job["shards"], executor.status(job["id"], job["paralelo"])):
            if sh["estado"] == "fechado":
                continue
            nome = sh["vm"]
            if st.get("estado") == "concluido":
                fim = (st.get("fim_vm") if st.get("vm") == "TERMINATED" else None) or ((st["fim"] + 30) if st.get("fim") else agora_)
                _fechar_shard(job, sh, (fim - (st.get("inicio_vm") or t0)) / 3600, st.get("codigo"), st.get("saida", ""), "concluido")
                executor.apagar_nome(nome)
            elif st.get("existe") and st.get("vm") == "TERMINATED":
                fim = st.get("fim_vm") or agora_
                _fechar_shard(job, sh, (fim - (st.get("inicio_vm") or t0)) / 3600, None,
                              "a VM parou antes de entregar o resultado (preempção spot?)", "parou")
                executor.apagar_nome(nome)
            elif not st.get("existe"):
                # Sumiu sem resultado: preempção (spot com DELETE) ou o Compute apagou no prazo. Não sabemos a hora
                # exata, então cobra até agora, limitado ao pedido: a conta nunca subestima.
                _fechar_shard(job, sh, (agora_ - t0) / 3600, None,
                              "a VM sumiu antes de entregar o resultado (preempção spot ou prazo do Compute)", "sumiu")
            elif estourou:
                executor.apagar_nome(nome)
                _fechar_shard(job, sh, job["horas"], None, "passou do prazo: a VM foi apagada e o tempo pedido foi cobrado", "prazo")
        if all(sh["estado"] == "fechado" for sh in job["shards"]):
            custo = round(max(sum(sh["custo_usd"] for sh in job["shards"]), 0.01), 4)   # ligar nunca é grátis
            creditos.confirmar(job["quem"], job["reserva"], custo)
            executor.apagar(job["id"], job["paralelo"])                                # redundante de propósito
            job.update(estado="liquidado", custo_usd=custo, liquidado=agora_,
                       horas_reais=round(sum(sh["horas_reais"] for sh in job["shards"]), 4),
                       codigo=max((sh["codigo"] for sh in job["shards"] if sh["codigo"] is not None), default=None))
        else:
            job["estado"] = "rodando"
        _gravar(job)
        return job

    def _arrumar() -> None:
        """Liquida o que acabou e apaga VM órfã (job fechado ou inexistente). Roda antes de toda tool do módulo."""
        jobs = {j["id"]: j for j in _todos()}
        for j in list(jobs.values()):
            if j["estado"] in ABERTOS:
                jobs[j["id"]] = _liquidar(j)
        for vm in executor.listar():
            j = jobs.get(vm["job"])
            if j is None or j["estado"] not in ABERTOS:
                executor.apagar_nome(vm["nome"])

    def _validar(tipo, horas, parametros, paralelo, maquina) -> str | None:
        if tipo not in TIPOS:
            return f"tipo inválido; use um de: {', '.join(TIPOS)}"
        if not 0 < horas <= TIPOS[tipo][1]:
            return f"horas tem de estar em (0, {TIPOS[tipo][1]}] para {tipo}"
        if not (isinstance(paralelo, int) and 1 <= paralelo <= paralelo_max):
            return f"paralelo tem de ser inteiro em [1, {paralelo_max}]"
        if maquina not in MAQUINAS:
            return f"máquina fora da lista; use uma de: {', '.join(MAQUINAS)}"
        commit = str(parametros.get("commit", "") or "")
        if commit and not COMMIT.fullmatch(commit):
            return "commit tem de ser um sha hexadecimal (7 a 40 caracteres) que já está na main"
        if tipo == "script":
            nome, conhecidos = str(parametros.get("nome", "")), scripts()
            if not NOME_SCRIPT.fullmatch(nome):
                return "script: `nome` é o nome de um arquivo de pesado/jobs/ sem o .sh (minúsculas, dígitos, - e _)"
            if conhecidos is not None and nome not in conhecidos:
                return f"script fora da allowlist (pesado/jobs/): use um de {conhecidos}"
        return None

    @tool
    def pesado_tipos() -> dict:
        """Tipos de trabalho pesado, teto de horas, máquinas aceitas com a tarifa por hora de cada VM (US$), o teto de
        `paralelo` e os scripts da allowlist (pesado/jobs/)."""
        return {"ok": True, "paralelo_max": paralelo_max, "maquina_padrao": maquina_padrao,
                "tarifas_hora_usd": {m: tarifa(m) for m in MAQUINAS}, "scripts": scripts(),
                "imagem": env.get("INF_PESADO_IMAGEM", "bkp-lean-build2-20261006"),
                "tipos": {k: {"descricao": d, "horas_max": h,
                              "custo_max_usd_por_vm": round(h * tarifa(maquina_padrao), 2)} for k, (d, h) in TIPOS.items()}}

    @tool
    def pesado(tipo: str, horas: float, parametros: dict | None = None, paralelo: int = 1, maquina: str = "",
               confirmar: bool = False) -> dict:
        """Pede trabalho pesado em `paralelo` VMs spot (shards 0..N-1). Sem confirmar=true só mostra o custo máximo
        (N × horas × tarifa) e o saldo (seco). Com confirmar=true reserva o custo máximo do lote inteiro, cria as VMs e
        devolve o `job`; acompanhe com `pesado_status`. Cobra-se o tempo real de cada VM; elas são apagadas no fim."""
        parametros = dict(parametros or {})
        maquina = maquina or maquina_padrao
        erro = _validar(tipo, horas, parametros, paralelo, maquina)
        if erro:
            return {"ok": False, "erro": erro}
        t = tarifa(maquina)
        custo = round(paralelo * horas * t, 4)
        _arrumar()
        saldo = creditos.saldo(ctx.quem())
        if not confirmar:
            return {"ok": True, "seco": True, "tipo": tipo, "paralelo": paralelo, "maquina": maquina,
                    "tarifa_hora_usd": t, "custo_maximo_usd": custo, "saldo": saldo,
                    "cabe": saldo["disponivel_usd"] is None or custo <= saldo["disponivel_usd"]}
        reserva = creditos.reservar(ctx.quem(), f"pesado:{tipo}", custo)     # o lote inteiro, antes de ligar nada
        job_id = uuid.uuid4().hex[:10]
        job = {"id": job_id, "quem": ctx.quem(), "tipo": tipo, "params": parametros, "horas": horas,
               "paralelo": paralelo, "maquina": maquina, "tarifa_hora_usd": t, "reserva": reserva,
               "reservado_usd": custo, "estado": "subindo", "iniciado": agora(),
               "shards": [{"i": i, "vm": f"inf-pesado-{job_id}-{i}", "estado": "pedido"} for i in range(paralelo)]}
        _gravar(job)                       # antes de criar: a varredura nunca confunde VM recém-criada com órfã
        try:
            info = executor.iniciar(job_id, tipo, parametros, horas, ctx.quem(), paralelo, maquina)
        except Exception as e:  # noqa: BLE001 - não rodou, não cobra
            creditos.cancelar(ctx.quem(), reserva)
            job.update(estado="nao_rodou", custo_usd=0.0, erro=str(e)[:300])
            _gravar(job)
            return {"ok": False, "erro": str(e) if isinstance(e, ErroCreditos) else f"executor falhou ({type(e).__name__}); reserva desfeita"}
        job.update(estado="pedido", info=info)
        _gravar(job)
        return {"ok": True, "seco": False, "job": job_id, "reservado_usd": custo, "vms": info,
                "proximo": "pesado_status(job) para ver o andamento; o custo real é cobrado quando cada VM termina"}

    @tool
    def pesado_status(job: str = "") -> dict:
        """Andamento dos seus jobs (ou de um `job`), shard a shard. Liquida o que terminou (cobra o tempo real, mostra
        código de saída e fim do log, e onde ficaram log e saída no bucket) e apaga VM que passou do prazo.
        Administrador vê o de qualquer pessoa."""
        _arrumar()
        if job:
            j = _ler(job)
            if not j or (j["quem"] != ctx.quem() and not creditos.e_admin(ctx.quem())):
                return {"ok": False, "erro": "job não encontrado"}
            jobs = [j]
        else:
            jobs = [j for j in _todos() if j["quem"] == ctx.quem() or creditos.e_admin(ctx.quem())]
            jobs = sorted(jobs, key=lambda j: j["iniciado"])[-10:]
        saida = []
        for j in jobs:
            r = {k: j.get(k) for k in ("id", "quem", "tipo", "estado", "paralelo", "maquina", "horas", "reservado_usd",
                                       "custo_usd", "horas_reais", "codigo", "erro") if k in j}
            r["shards"] = [{k: s.get(k) for k in ("i", "estado", "motivo", "horas_reais", "custo_usd", "codigo", "saida")
                            if k in s} for s in j.get("shards", [])]
            r["bucket"] = f"{JOBS}{j['id']}/ (shard-<i>.txt sempre; shard-<i>.log e shard-<i>-saida.tar.gz se a VM subiu)"
            saida.append(r)
        return {"ok": True, "jobs": saida}

