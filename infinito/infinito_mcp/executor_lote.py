"""Executor de LOTE do trabalho pesado: N VMs spot efêmeras por job, criadas de uma imagem e APAGADAS no fim.

Substitui o executor da VM fixa `lean-build2` (apagada em 2026-10-06; sobrou a imagem `bkp-lean-build2-20261006`).
Cada shard `i` de um job vira a instância `inf-pesado-<job>-<i>`:

* criada **spot** com `instanceTerminationAction=DELETE` e `maxRunDuration = horas + 10 min`: o próprio Compute apaga a
  máquina no estouro do prazo, mesmo que ninguém consulte o job (a trava não depende do servidor estar de pé);
* sem service account: a VM não tem credencial nenhuma. Log e saída sobem por **URL assinada** de PUT para um objeto
  exato do bucket de estado (`jobs/<job>/shard-<i>.log` e `...-saida.tar.gz`), válida só até o prazo. Sem permissão de
  assinar, o job roda igual e volta só o fim do log pelos *guest attributes* (o comportamento antigo);
* o script da VM (vm/lote.sh) só conhece a allowlist e só roda commit que já está na `main`;
* rótulo `infinito-pesado=1` + `infinito-job=<job>`: a varredura (`listar`) acha órfã e o módulo apaga.

Antes de criar qualquer coisa, confere a cota do projeto (CPUs, endereços, disco, instâncias) e recusa se não cabe:
medido em 2026-10-06, o limite de IPs externos da região (8, 2 em uso) é o que trava primeiro, não as CPUs.
Se a criação do shard k falha, apaga os k-1 já criados: ou o lote inteiro sobe, ou nada fica ligado.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode, b64encode
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .creditos import ErroCreditos
from .gcp import token_metadata

COMPUTE = "https://compute.googleapis.com/compute/v1/projects/{p}"
SCRIPT = Path(__file__).with_name("vm") / "lote.sh"
PREFIXO = "inf-pesado-"
PRAZO_EXTRA_S = 600            # maxRunDuration = horas + 10 min: dá tempo de o script subir o log antes do Compute apagar
Http = Callable[[str, str, dict | None], tuple[int, dict]]
Assinador = Callable[[str, int], str | None]     # (objeto, segundos) -> URL de PUT, ou None sem permissão

# vCPU e GiB de cada tipo aceito (allowlist: o agente não escolhe máquina fora daqui).
MAQUINAS = {
    "e2-standard-4": (4, 16), "e2-standard-8": (8, 32), "e2-standard-16": (16, 64),
    "e2-highmem-4": (4, 32), "e2-highmem-8": (8, 64), "e2-highmem-16": (16, 128),
    "e2-highcpu-8": (8, 8), "e2-highcpu-16": (16, 16), "e2-highcpu-32": (32, 32),
    "c2d-standard-8": (8, 32), "c2d-highmem-8": (8, 64), "c2d-highcpu-16": (16, 32),
}
# US$/h por vCPU e por GiB, SPOT, southamerica-east1, lidos da Cloud Billing Catalog API em 2026-10-06
# (SKUs "Spot Preemptible E2 Instance Core/Ram running in Sao Paulo" e os de C2D). Disco e IP à parte.
PRECO_SPOT = {"e2": (0.00761, 0.001019), "c2d": (0.00873, 0.001166)}
PRECO_DISCO_GB_MES = {"pd-standard": 0.06, "pd-balanced": 0.15}    # "Storage/Balanced PD Capacity in Sao Paulo"
PRECO_IP_H = 0.005                                                 # IPv4 externo em uso (tabela pública do VPC)


def tarifa_hora(maquina: str, disco_gb: int = 100, tipo_disco: str = "pd-balanced", margem: float = 1.2) -> float:
    """US$/h de UM shard: núcleo + memória spot + disco + IP, vezes a margem (preço spot muda até uma vez por mês;
    o teto só vale se a tarifa não subestimar)."""
    cpu, mem = MAQUINAS[maquina]
    p_cpu, p_mem = PRECO_SPOT[maquina.split("-")[0]]
    h = cpu * p_cpu + mem * p_mem + disco_gb * PRECO_DISCO_GB_MES[tipo_disco] / 730 + PRECO_IP_H
    return round(h * margem, 4)


def _http(metodo: str, url: str, corpo: dict | None, token: Callable[[], str] = token_metadata) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=None if corpo is None else json.dumps(corpo).encode(), method=metodo,
                                 headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read()
            return r.status, json.loads(t) if t.strip() else {}
    except urllib.error.HTTPError as e:
        t = e.read()
        try:
            return e.code, json.loads(t)
        except ValueError:
            return e.code, {"bruto": t[:300].decode(errors="replace")}


def _epoch(rfc3339: str | None) -> float | None:
    return datetime.fromisoformat(rfc3339).timestamp() if rfc3339 else None


# ------------------------------------------------------------------ URL assinada (V4) sem chave
def assinar_put_v4(bucket: str, objeto: str, segundos: int, email: str, assinar_bytes: Callable[[bytes], bytes],
                   agora: datetime | None = None) -> str:
    """URL V4 de PUT para UM objeto, assinada pela própria SA do serviço (IAM signBlob: nenhuma chave existe).
    Formato da documentação 'Signing URLs manually' do Cloud Storage."""
    agora = agora or datetime.now(timezone.utc)
    data, quando = agora.strftime("%Y%m%d"), agora.strftime("%Y%m%dT%H%M%SZ")
    escopo = f"{data}/auto/storage/goog4_request"
    q = {"X-Goog-Algorithm": "GOOG4-RSA-SHA256", "X-Goog-Credential": f"{email}/{escopo}", "X-Goog-Date": quando,
         "X-Goog-Expires": str(min(int(segundos), 604800)), "X-Goog-SignedHeaders": "host"}
    consulta = "&".join(f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}" for k, v in sorted(q.items()))
    caminho = "/" + urllib.parse.quote(f"{bucket}/{objeto}", safe="/-_.~")
    canonico = f"PUT\n{caminho}\n{consulta}\nhost:storage.googleapis.com\n\nhost\nUNSIGNED-PAYLOAD"
    a_assinar = f"GOOG4-RSA-SHA256\n{quando}\n{escopo}\n{hashlib.sha256(canonico.encode()).hexdigest()}"
    assinatura = assinar_bytes(a_assinar.encode()).hex()
    return f"https://storage.googleapis.com{caminho}?{consulta}&X-Goog-Signature={assinatura}"


def assinador_da_sa(bucket: str, http: Http = _http) -> Assinador:
    """Assina com a SA do Cloud Run pelo IAM Credentials (`iam.serviceAccounts.signBlob` nela mesma). Sem a permissão
    devolve None: o job roda e o resultado volta pelos guest attributes (3 KB), nunca finge que subiu o log."""
    def email() -> str:
        req = urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
                                     headers={"Metadata-Flavor": "Google"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode().strip()

    def assinar(objeto: str, segundos: int) -> str | None:
        try:
            sa = email()

            def blob(b: bytes) -> bytes:
                st, d = http("POST", f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{sa}:signBlob",
                             {"payload": b64encode(b).decode()})
                if st != 200:
                    raise PermissionError(f"signBlob HTTP {st}")
                return b64decode(d["signedBlob"])
            return assinar_put_v4(bucket, objeto, segundos, sa, blob)
        except Exception:  # noqa: BLE001 - sem assinatura o job continua, com resultado menor
            return None
    return assinar


# ------------------------------------------------------------------------------- o executor
class ExecutorLote:
    def __init__(self, projeto: str, zona: str = "southamerica-east1-a", imagem: str = "bkp-lean-build2-20261006",
                 http: Http | None = None, assinador: Assinador | None = None, disco_gb: int = 100,
                 tipo_disco: str = "pd-balanced", dormir: Callable[[float], None] = time.sleep):
        self.projeto, self.zona, self.regiao = projeto, zona, zona.rsplit("-", 1)[0]
        self.imagem = imagem if "/" in imagem else f"projects/{projeto}/global/images/{imagem}"
        self.base = COMPUTE.format(p=projeto)
        self._http, self._assinar, self._dormir = http or _http, assinador or (lambda o, s: None), dormir
        self.disco_gb, self.tipo_disco = disco_gb, tipo_disco

    @staticmethod
    def nome(job_id: str, i: int) -> str:
        return f"{PREFIXO}{job_id}-{i}"

    def _inst(self, nome: str = "") -> str:
        return f"{self.base}/zones/{self.zona}/instances" + (f"/{nome}" if nome else "")

    # --------------------------------------------------------------- cota antes de tudo
    def checar_cota(self, n: int, maquina: str) -> None:
        cpu = MAQUINAS[maquina][0]
        pede = {"CPUS": n * cpu, "INSTANCES": n, "IN_USE_ADDRESSES": n,
                ("SSD_TOTAL_GB" if self.tipo_disco == "pd-balanced" else "DISKS_TOTAL_GB"): n * self.disco_gb}
        faltas = []
        for url, metricas in ((f"{self.base}/regions/{self.regiao}", pede), (self.base, {"CPUS_ALL_REGIONS": n * cpu})):
            st, d = self._http("GET", url, None)
            if st != 200:
                return            # sem permissão de ler cota: a criação ainda devolve QUOTA_EXCEEDED, e aí desfaz
            cotas = {q["metric"]: q for q in d.get("quotas", [])}
            for m, quer in metricas.items():
                q = cotas.get(m)
                if q and q["usage"] + quer > q["limit"]:
                    faltas.append(f"{m}: pede {quer}, livre {q['limit'] - q['usage']:g}")
        if faltas:
            raise ErroCreditos("não cabe na cota do projeto (" + "; ".join(faltas) + "). Diminua `paralelo` ou peça "
                               "ao dono para subir a cota. Nada foi cobrado")

    # ------------------------------------------------------------------- criar e apagar
    def _corpo(self, job: dict, i: int, maquina: str, segundos: int, urls: dict) -> dict:
        meta = {"startup-script": SCRIPT.read_text(), "enable-guest-attributes": "TRUE",
                "infinito-job": json.dumps({**job, "shard": i, **urls}, ensure_ascii=False)}
        return {
            "name": self.nome(job["id"], i), "machineType": f"zones/{self.zona}/machineTypes/{maquina}",
            "labels": {"infinito-pesado": "1", "infinito-job": job["id"]},
            "scheduling": {"provisioningModel": "SPOT", "instanceTerminationAction": "DELETE",
                           "maxRunDuration": {"seconds": segundos}, "automaticRestart": False,
                           "onHostMaintenance": "TERMINATE"},
            "disks": [{"boot": True, "autoDelete": True, "initializeParams": {
                "sourceImage": self.imagem, "diskSizeGb": str(self.disco_gb),
                "diskType": f"zones/{self.zona}/diskTypes/{self.tipo_disco}"}}],
            "networkInterfaces": [{"network": "global/networks/default",
                                   "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "externo"}]}],
            "metadata": {"items": [{"key": k, "value": v} for k, v in meta.items()]},
        }

    def _erro_da_operacao(self, st: int, op: dict) -> str | None:
        """O insert pode devolver 200 com o erro (cota, capacidade spot) DENTRO da operação."""
        if st >= 400:
            return f"HTTP {st}: {json.dumps(op)[:200]}"
        for _ in range(5):
            erros = (op.get("error") or {}).get("errors") or []
            if erros:
                return "; ".join(f"{e.get('code')}: {e.get('message', '')[:140]}" for e in erros)
            if op.get("status") == "DONE" or not op.get("selfLink"):
                return None
            st, novo = self._http("GET", op["selfLink"], None)
            if st != 200:
                return None
            op = novo
            self._dormir(2)
        return None

    def iniciar(self, job_id: str, tipo: str, parametros: dict, horas: float, quem: str, paralelo: int,
                maquina: str) -> dict:
        self.checar_cota(paralelo, maquina)
        segundos = int(horas * 3600) + PRAZO_EXTRA_S
        job = {"id": job_id, "tipo": tipo, "params": parametros, "horas": horas, "quem": quem, "total": paralelo}
        criados, sem_log = [], 0
        for i in range(paralelo):
            urls = {"url_log": self._assinar(f"jobs/{job_id}/shard-{i}.log", segundos),
                    "url_saida": self._assinar(f"jobs/{job_id}/shard-{i}-saida.tar.gz", segundos)}
            sem_log += urls["url_log"] is None
            st, op = self._http("POST", self._inst(), self._corpo(job, i, maquina, segundos, urls))
            erro = self._erro_da_operacao(st, op)
            if erro:
                self.apagar(job_id, len(criados) + 1)          # o que subiu (e o meio-criado) cai junto
                raise ErroCreditos(f"o shard {i} não subiu ({erro}); os {len(criados)} já criados foram apagados. "
                                   "Nada foi cobrado")
            criados.append(self.nome(job_id, i))
        return {"vms": criados, "maquina": maquina, "prazo_s": segundos, "log_no_bucket": sem_log == 0}

    def apagar(self, job_id: str, total: int) -> None:
        for i in range(total):
            self._http("DELETE", self._inst(self.nome(job_id, i)), None)     # 404 = já não existe: tudo bem

    def apagar_nome(self, nome: str) -> None:
        if nome.startswith(PREFIXO):                                          # nunca apaga VM que não é do Infinito
            self._http("DELETE", self._inst(nome), None)

    # ------------------------------------------------------------------------- leitura
    def status(self, job_id: str, total: int) -> list[dict]:
        saida = []
        for i in range(total):
            nome = self.nome(job_id, i)
            st, inst = self._http("GET", self._inst(nome), None)
            if st == 404:
                saida.append({"existe": False})
                continue
            if st != 200:
                raise ErroCreditos(f"lote: GET {nome} -> HTTP {st}")
            sg, ga = self._http("GET", self._inst(nome) + "/getGuestAttributes?queryPath=infinito/", None)
            attrs = {a["key"]: a["value"] for a in (ga.get("queryValue", {}).get("items", []) if sg == 200 else [])}
            meu = attrs.get("id") == job_id
            saida.append({"existe": True, "vm": inst.get("status"), "inicio_vm": _epoch(inst.get("lastStartTimestamp")),
                          "fim_vm": _epoch(inst.get("lastStopTimestamp")),
                          "estado": attrs.get("estado") if meu else None,
                          "codigo": int(attrs["codigo"]) if meu and "codigo" in attrs else None,
                          "saida": attrs.get("saida", "") if meu else "",
                          "fim": float(attrs["fim"]) if meu and "fim" in attrs else None})
        return saida

    def listar(self) -> list[dict]:
        """Todas as VMs do Infinito na zona (rótulo), para a varredura de órfãs."""
        filtro = urllib.parse.quote("labels.infinito-pesado=1")
        st, d = self._http("GET", f"{self._inst()}?filter={filtro}", None)
        if st != 200:
            return []
        return [{"nome": i["name"], "job": i.get("labels", {}).get("infinito-job", ""), "status": i.get("status")}
                for i in d.get("items", [])]
