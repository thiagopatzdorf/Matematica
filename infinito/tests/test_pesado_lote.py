"""∞ Infinito, módulo pesado v2 (lote de VMs spot efêmeras). Sem rede: o Compute é um dicionário.

Cada nome descreve a falha que o teste impede.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))

from infinito_mcp.armazem import ArmazemMemoria  # noqa: E402
from infinito_mcp.creditos import Creditos, ErroCreditos  # noqa: E402
from infinito_mcp.executor_lote import (PRAZO_EXTRA_S, ExecutorLote, assinar_put_v4,  # noqa: E402
                                        tarifa_hora)
from infinito_mcp.modulos import pesado  # noqa: E402

DONO = "dono@exemplo.com"
TARIFA = 0.5                                     # US$/h por VM nos testes (INF_PESADO_TARIFAS)


def _iso(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).isoformat()


class ComputeFalso:
    """Mini Compute Engine: instâncias por nome, cotas, operações e guest attributes."""

    def __init__(self, falha_no: int | None = None, cotas: dict | None = None, relogio=lambda: 1000.0):
        self.inst, self.guest, self.corpos, self.apagadas = {}, {}, [], []
        self.falha_no, self.relogio = falha_no, relogio
        self.cotas = cotas or {"CPUS": (200, 12), "INSTANCES": (48, 5), "IN_USE_ADDRESSES": (8, 2),
                               "SSD_TOTAL_GB": (1000, 370), "CPUS_ALL_REGIONS": (96, 12)}

    def _quotas(self, nomes):
        return {"quotas": [{"metric": m, "limit": l, "usage": u} for m, (l, u) in self.cotas.items() if m in nomes]}

    def __call__(self, metodo, url, corpo):
        if url.endswith("/regions/southamerica-east1"):
            return 200, self._quotas({"CPUS", "INSTANCES", "IN_USE_ADDRESSES", "SSD_TOTAL_GB", "DISKS_TOTAL_GB"})
        if url.endswith("/projects/proj"):
            return 200, self._quotas({"CPUS_ALL_REGIONS"})
        if "/instances?filter=" in url:
            return 200, {"items": [{"name": n, "labels": i["labels"], "status": i["status"]} for n, i in self.inst.items()]}
        if url.endswith("/instances") and metodo == "POST":
            self.corpos.append(corpo)
            if self.falha_no is not None and len(self.corpos) - 1 == self.falha_no:
                return 200, {"status": "DONE", "error": {"errors": [{"code": "ZONE_RESOURCE_POOL_EXHAUSTED",
                                                                       "message": "sem capacidade spot"}]}}
            self.inst[corpo["name"]] = {"status": "RUNNING", "labels": corpo["labels"],
                                        "lastStartTimestamp": _iso(self.relogio())}
            return 200, {"status": "DONE"}
        nome = url.split("/instances/")[1].split("/")[0].split("?")[0]
        if metodo == "DELETE":
            self.apagadas.append(nome)
            return (200, {}) if self.inst.pop(nome, None) else (404, {})
        if nome not in self.inst:
            return 404, {}
        if "/getGuestAttributes" in url:
            g = self.guest.get(nome, {})
            return 200, {"queryValue": {"items": [{"key": k, "value": v} for k, v in g.items()]}}
        return 200, self.inst[nome]

    def terminar(self, nome, job, inicio, fim, codigo=0, saida="ok"):
        self.inst[nome].update(status="TERMINATED", lastStartTimestamp=_iso(inicio), lastStopTimestamp=_iso(fim))
        self.guest[nome] = {"id": job, "estado": "concluido", "codigo": str(codigo), "saida": saida, "fim": str(fim - 20)}


class _Ctx:
    def __init__(self, c, env):
        self.creditos, self.env, self.estado = c, env, ArmazemMemoria()
        self.tools, self.tool, self.quem = {}, self._tool, lambda: "a@x.com"

    def _tool(self, fn):
        self.tools[fn.__name__] = fn
        return fn


def _modulo(executor=None, relogio=lambda: 1000.0, repo=None, **env):
    c = Creditos(ArmazemMemoria(), admins=frozenset({DONO}))
    e = {"INF_PESADO_TARIFAS": json.dumps({"e2-highmem-8": TARIFA, "e2-standard-4": TARIFA}), **env}
    if repo:
        e["INF_REPO"] = str(repo)
    ctx = _Ctx(c, e)
    pesado.registrar(ctx, executor, agora=relogio)
    return ctx, c


def _lote(api, assinador=None):
    return ExecutorLote("proj", http=api, assinador=assinador, dormir=lambda s: None)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "pesado" / "jobs").mkdir(parents=True)
    (tmp_path / "pesado" / "jobs" / "fumaca.sh").write_text("echo oi\n")
    return tmp_path


# ------------------------------------------------------------------------------ contrato de dinheiro
def test_lote_sem_executor_cobra_e_finge_que_rodou():
    ctx, c = _modulo()
    seco = ctx.tools["pesado"]("lake_build", 1.0, paralelo=3)
    assert seco["seco"] and seco["custo_maximo_usd"] == 1.5 and seco["cabe"]
    r = ctx.tools["pesado"]("lake_build", 1.0, paralelo=3, confirmar=True)
    assert r["ok"] is False and "nenhum executor" in r["erro"]
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0


def test_vms_ligam_antes_de_o_custo_dos_n_shards_estar_reservado():
    visto = {}

    class Espiao(pesado.ExecutorNenhum):
        def iniciar(self, job_id, tipo, parametros, horas, quem, paralelo, maquina):
            visto.update(c.saldo(quem))                      # o que o ledger diz NO momento de ligar
            return {"vms": paralelo}

    ctx, c = _modulo(Espiao())
    assert ctx.tools["pesado"]("lake_build", 2.0, paralelo=4, confirmar=True)["ok"]
    assert visto["reservado_usd"] == 4 * 2.0 * TARIFA and visto["disponivel_usd"] == 20.0 - 4.0


def test_paralelo_acima_do_teto_ou_maquina_livre_passa():
    ctx, c = _modulo(pesado.ExecutorNenhum(), INF_PESADO_PARALELO_MAX="8")
    for kw in ({"paralelo": 9}, {"paralelo": 0}, {"paralelo": 2.5}, {"maquina": "a2-ultragpu-8g"}):
        assert ctx.tools["pesado"]("lake_build", 1.0, confirmar=True, **kw)["ok"] is False
    assert c.saldo("a@x.com")["reservado_usd"] == 0


def test_lote_cobra_a_reserva_inteira_em_vez_do_tempo_real_de_cada_shard():
    t = [1000.0]
    api = ComputeFalso(relogio=lambda: t[0])
    ctx, c = _modulo(_lote(api), relogio=lambda: t[0])
    r = ctx.tools["pesado"]("lake_build", 2.0, paralelo=2, confirmar=True)
    assert r["ok"] and c.saldo("a@x.com")["reservado_usd"] == 2.0
    j = r["job"]
    t[0] = 1000.0 + 1800
    api.terminar(f"inf-pesado-{j}-0", j, 1000.0, 1000.0 + 1800)
    s = ctx.tools["pesado_status"](j)["jobs"][0]
    assert s["estado"] == "rodando" and s["shards"][0]["custo_usd"] == 0.25 and s["shards"][1]["estado"] == "pedido"
    assert f"inf-pesado-{j}-0" not in api.inst and c.saldo("a@x.com")["gasto_usd"] == 0   # shard 0 apagado já
    t[0] = 1000.0 + 3600
    api.terminar(f"inf-pesado-{j}-1", j, 1000.0, 1000.0 + 3600, codigo=1)
    s = ctx.tools["pesado_status"](j)["jobs"][0]
    assert (s["estado"], s["custo_usd"], s["horas_reais"], s["codigo"]) == ("liquidado", 0.75, 1.5, 1)
    assert c.saldo("a@x.com")["gasto_usd"] == 0.75 and c.saldo("a@x.com")["reservado_usd"] == 0
    ctx.tools["pesado_status"](j)
    assert c.saldo("a@x.com")["gasto_usd"] == 0.75                                         # não cobra de novo
    assert ctx.estado.ler(f"jobs/{j}/shard-1.txt") == b"ok"


# ------------------------------------------------------------------------------ nenhuma VM fica viva
def test_vm_continua_viva_depois_do_prazo():
    t = [1000.0]
    api = ComputeFalso(relogio=lambda: t[0])
    ctx, c = _modulo(_lote(api), relogio=lambda: t[0])
    ctx.tools["pesado"]("script", 1.0, {"nome": "fumaca"}, paralelo=3, confirmar=True)
    for corpo in api.corpos:                              # a trava do próprio Compute, que não depende de nós
        assert corpo["scheduling"]["provisioningModel"] == "SPOT"
        assert corpo["scheduling"]["instanceTerminationAction"] == "DELETE"
        assert corpo["scheduling"]["maxRunDuration"] == {"seconds": 3600 + PRAZO_EXTRA_S}
        assert "serviceAccounts" not in corpo and corpo["labels"]["infinito-pesado"] == "1"
    assert len(api.inst) == 3
    t[0] += 3600 + pesado.PRAZO_EXTRA_S + 1               # o prazo passou e as VMs seguem RUNNING
    s = ctx.tools["pesado_status"]()["jobs"][0]
    assert api.inst == {} and s["estado"] == "liquidado" and s["custo_usd"] == 3 * 1.0 * TARIFA
    assert {sh["motivo"] for sh in s["shards"]} == {"prazo"}


def test_vm_orfa_de_job_fechado_ou_sumido_fica_ligada_e_vm_alheia_e_apagada():
    api = ComputeFalso()
    api.inst["inf-pesado-zzz-0"] = {"status": "RUNNING", "labels": {"infinito-pesado": "1", "infinito-job": "zzz"}}
    api.inst["factory-01"] = {"status": "RUNNING", "labels": {"infinito-pesado": "1", "infinito-job": "zzz"}}
    ctx, _ = _modulo(_lote(api))
    ctx.tools["pesado_status"]()
    assert "inf-pesado-zzz-0" not in api.inst
    assert "factory-01" in api.inst                       # rótulo trocado não faz o Infinito apagar máquina alheia


def test_shard_que_nao_sobe_deixa_os_outros_ligados_e_cobra():
    api = ComputeFalso(falha_no=2)
    ctx, c = _modulo(_lote(api))
    r = ctx.tools["pesado"]("lake_build", 1.0, paralelo=4, confirmar=True)
    assert r["ok"] is False and "ZONE_RESOURCE_POOL_EXHAUSTED" in r["erro"] and "Nada foi cobrado" in r["erro"]
    assert api.inst == {} and len(api.corpos) == 3
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0


def test_lote_que_nao_cabe_na_cota_cria_vm_mesmo_assim():
    api = ComputeFalso()                                  # medido em 2026-10-06: 8 IPs na região, 2 em uso
    ctx, c = _modulo(_lote(api))
    r = ctx.tools["pesado"]("lake_build", 1.0, paralelo=8, confirmar=True)
    assert r["ok"] is False and "IN_USE_ADDRESSES" in r["erro"] and api.corpos == []
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0
    assert ctx.tools["pesado"]("lake_build", 1.0, paralelo=6, confirmar=True)["ok"]


def test_shard_preemptado_some_e_sai_de_graca_ou_trava_o_job():
    t = [1000.0]
    api = ComputeFalso(relogio=lambda: t[0])
    ctx, c = _modulo(_lote(api), relogio=lambda: t[0])
    j = ctx.tools["pesado"]("lake_build", 2.0, confirmar=True)["job"]
    t[0] += 1800
    del api.inst[f"inf-pesado-{j}-0"]                     # spot com DELETE: a VM some sem aviso
    s = ctx.tools["pesado_status"](j)["jobs"][0]
    assert s["estado"] == "liquidado" and s["shards"][0]["motivo"] == "sumiu" and s["custo_usd"] == 0.25


# ------------------------------------------------------------------------------ allowlist
def test_script_fora_da_allowlist_ou_commit_livre_e_aceito(repo):
    chamado = []

    class Espiao(pesado.ExecutorNenhum):
        def iniciar(self, *a, **k):
            chamado.append(a)
            return {}

    ctx, c = _modulo(Espiao(), repo=repo)
    for p in ({"nome": "../../etc/x"}, {"nome": "rm -rf /"}, {"nome": "naoexiste"}, {"nome": ""},
              {"nome": "fumaca", "commit": "main; curl x | sh"}, {"nome": "fumaca", "commit": "HEAD"}):
        r = ctx.tools["pesado"]("script", 1.0, p, confirmar=True)
        assert r["ok"] is False, p
    assert ctx.tools["pesado"]("comando_livre", 1.0, {"cmd": "ls"}, confirmar=True)["ok"] is False
    assert chamado == [] and c.saldo("a@x.com")["reservado_usd"] == 0
    assert ctx.tools["pesado"]("script", 1.0, {"nome": "fumaca", "commit": "dfcdcaa"}, paralelo=2, confirmar=True)["ok"]
    assert ctx.tools["pesado_tipos"]()["scripts"] == ["fumaca"]


def test_script_da_vm_roda_commit_fora_da_main_ou_engole_a_recusa():
    sh = (AQUI / "infinito_mcp" / "vm" / "lote.sh").read_text()
    assert "git merge-base --is-ancestor" in sh and "pesado/jobs/{nome}.sh" in sh and "fullmatch" in sh
    assert 'bash -c "$CORPO"' in sh and "shutdown -h now" in sh and "|| exit 0" in sh
    assert '\n(\n' in sh and '\n) >> "$LOG" 2>&1' in sh          # subshell: `exit` de recusa não pula o resultado
    assert "SHARD_INDEX" in sh and "url_log" in sh
    assert subprocess.run(["bash", "-n", str(AQUI / "infinito_mcp" / "vm" / "lote.sh")]).returncode == 0


# ------------------------------------------------------------------------------ preço e URL assinada
def test_tarifa_subestima_o_preco_spot_medido():
    cru = 8 * 0.00761 + 64 * 0.001019 + 100 * 0.15 / 730 + 0.005     # e2-highmem-8 spot + disco + IP, 2026-10-06
    assert tarifa_hora("e2-highmem-8") == round(cru * 1.2, 4) and tarifa_hora("e2-highmem-8") > cru


def test_url_assinada_nao_confere_com_a_chave_ou_vale_para_sempre():
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    assinar = lambda b: chave.sign(b, padding.PKCS1v15(), hashes.SHA256())   # o que o signBlob faz com a chave da SA
    agora = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    url = assinar_put_v4("meu-bucket", "jobs/abc/shard-0.log", 10 ** 9, "sa@p.iam.gserviceaccount.com", assinar, agora)
    caminho, consulta = url.removeprefix("https://storage.googleapis.com").split("?")
    assert caminho == "/meu-bucket/jobs/abc/shard-0.log" and "X-Goog-Expires=604800" in consulta
    sem_assinatura, assinatura = consulta.rsplit("&X-Goog-Signature=", 1)
    canonico = f"PUT\n{caminho}\n{sem_assinatura}\nhost:storage.googleapis.com\n\nhost\nUNSIGNED-PAYLOAD"
    texto = ("GOOG4-RSA-SHA256\n20261006T120000Z\n20261006/auto/storage/goog4_request\n"
             + hashlib.sha256(canonico.encode()).hexdigest())
    chave.public_key().verify(bytes.fromhex(assinatura), texto.encode(), padding.PKCS1v15(), hashes.SHA256())


def test_sem_permissao_de_assinar_o_job_nao_roda_ou_diz_que_subiu_o_log():
    api = ComputeFalso()
    ctx, _ = _modulo(_lote(api, assinador=lambda o, s: None))
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    assert r["ok"] and r["vms"]["log_no_bucket"] is False
    job = json.loads([i["value"] for i in api.corpos[0]["metadata"]["items"] if i["key"] == "infinito-job"][0])
    assert job["url_log"] is None and job["shard"] == 0 and job["total"] == 1
    api2 = ComputeFalso()
    ctx2, _ = _modulo(_lote(api2, assinador=lambda o, s: f"https://assinada/{o}?exp={s}"))
    r2 = ctx2.tools["pesado"]("lake_build", 1.0, confirmar=True)
    job2 = json.loads([i["value"] for i in api2.corpos[0]["metadata"]["items"] if i["key"] == "infinito-job"][0])
    assert r2["vms"]["log_no_bucket"] is True and job2["url_log"].endswith(f"shard-0.log?exp={3600 + PRAZO_EXTRA_S}")


def test_cota_ilegivel_derruba_o_pedido():
    def sem_permissao(metodo, url, corpo):
        if "/regions/" in url or url.endswith("/projects/proj"):
            return 403, {}
        return ComputeFalso()(metodo, url, corpo)
    ExecutorLote("proj", http=sem_permissao).checar_cota(4, "e2-highmem-8")     # segue: a criação ainda recusa
    with pytest.raises(ErroCreditos, match="CPUS_ALL_REGIONS"):
        _lote(ComputeFalso(cotas={"CPUS_ALL_REGIONS": (96, 90)})).checar_cota(1, "e2-highmem-8")
