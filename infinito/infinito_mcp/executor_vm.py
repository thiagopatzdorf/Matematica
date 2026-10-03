"""Executor de trabalho pesado: liga a VM `lean-build2` com UM job, lê o resultado, e deixa a conta para o ledger.

Desenho (2026-10-03, "sim, liga"): a VM é uma e2-highmem-8 sem service account, desligada. O executor
(a) põe nos metadados o `startup-script` (vm/job.sh) e o `infinito-job` (tipo + parâmetros; allowlist),
(b) liga, (c) lê o resultado pelos *guest attributes* que o próprio script escreve, e (d) desliga se o tempo estourar.

Travas, nesta ordem:
* **uma VM, um job**: se ela não está TERMINATED, recusa ("ocupada"). Ninguém empilha custo;
* o script da VM roda `timeout` com as horas pedidas e desliga a máquina ao terminar;
* `maxRunDuration` (+10 min) no agendamento da VM, como segundo paraquedas, e `parar()` pelo executor quando alguém
  consulta o job depois do prazo;
* o papel da SA do serviço é `compute.instanceAdmin.v1` SÓ nessa instância (nada no projeto).

O que NÃO existe: arquivo de resultado (a VM não tem credencial de armazenamento). O que volta é o código de saída e
os últimos 3 KB do log. Resultado maior (um código achado numa busca) pede uma credencial própria para a VM: decisão
do Thiago, e é a razão de `busca` não estar entre os tipos.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from .creditos import ErroCreditos
from .gcp import token_metadata

COMPUTE = "https://compute.googleapis.com/compute/v1/projects/{p}/zones/{z}/instances/{i}"
SCRIPT = Path(__file__).with_name("vm") / "job.sh"
Http = Callable[[str, str, dict | None], tuple[int, dict]]


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
    if not rfc3339:
        return None
    from datetime import datetime
    return datetime.fromisoformat(rfc3339).timestamp()


class ExecutorVM:
    def __init__(self, projeto: str, zona: str = "southamerica-east1-a", instancia: str = "lean-build2",
                 http: Http | None = None, dormir: Callable[[float], None] = time.sleep):
        self.url = COMPUTE.format(p=projeto, z=zona, i=instancia)
        self._http, self._dormir = http or _http, dormir

    def _pedir(self, metodo: str, caminho: str = "", corpo: dict | None = None) -> dict:
        st, d = self._http(metodo, self.url + caminho, corpo)
        if st >= 400:
            raise ErroCreditos(f"VM: {metodo} {caminho or 'instância'} -> HTTP {st}: {json.dumps(d)[:160]}")
        return d

    def _esperar(self, ok: Callable[[dict], bool], rotulo: str, tentativas: int = 20) -> dict:
        for _ in range(tentativas):
            d = self._pedir("GET")
            if ok(d):
                return d
            self._dormir(3)
        raise ErroCreditos(f"VM: {rotulo} não aconteceu a tempo")

    def _metadados(self, inst: dict, **mudar: str | None) -> None:
        itens = {i["key"]: i["value"] for i in inst.get("metadata", {}).get("items", [])}
        for k, v in mudar.items():
            itens.pop(k, None) if v is None else itens.__setitem__(k, v)
        self._pedir("POST", "/setMetadata", {"fingerprint": inst["metadata"]["fingerprint"],
                                              "items": [{"key": k, "value": v} for k, v in itens.items()]})

    def iniciar(self, tipo: str, parametros: dict, horas: float, quem: str, job_id: str = "") -> dict:
        inst = self._pedir("GET")
        if inst["status"] != "TERMINATED":
            raise ErroCreditos(f"a VM está ocupada ({inst['status']}): um job por vez, tente de novo mais tarde")
        job = json.dumps({"id": job_id, "tipo": tipo, "params": parametros, "horas": horas, "quem": quem})
        self._metadados(inst, **{"startup-script": SCRIPT.read_text(), "infinito-job": job,
                                 "enable-guest-attributes": "TRUE"})
        self._esperar(lambda d: any(i["key"] == "infinito-job" for i in d.get("metadata", {}).get("items", [])),
                      "gravar o job nos metadados")
        paraquedas = True
        try:
            self._pedir("POST", "/setScheduling", {"onHostMaintenance": "MIGRATE", "automaticRestart": True,
                                                     "instanceTerminationAction": "STOP",
                                                     "maxRunDuration": {"seconds": int(horas * 3600) + 600}})
        except ErroCreditos:
            paraquedas = False        # o `timeout` + shutdown do script e o parar() do executor continuam valendo
        self._pedir("POST", "/start")
        self._esperar(lambda d: d["status"] in ("PROVISIONING", "STAGING", "RUNNING"), "ligar")
        return {"vm": "ligando", "paraquedas_maxrunduration": paraquedas}

    def status(self, job_id: str) -> dict:
        inst = self._pedir("GET")
        st, ga = self._http("GET", self.url + "/getGuestAttributes?queryPath=infinito/", None)
        attrs = {i["key"]: i["value"] for i in (ga.get("queryValue", {}).get("items", []) if st == 200 else [])}
        meu = attrs.get("id") == job_id
        return {"vm": inst["status"], "inicio_vm": _epoch(inst.get("lastStartTimestamp")),
                "fim_vm": _epoch(inst.get("lastStopTimestamp")),
                "estado": attrs.get("estado") if meu else None, "codigo": int(attrs["codigo"]) if meu and "codigo" in attrs else None,
                "saida": attrs.get("saida", "") if meu else "", "fim": float(attrs["fim"]) if meu and "fim" in attrs else None}

    def parar(self) -> None:
        self._pedir("POST", "/stop")

    def liberar(self) -> None:
        """Tira o job dos metadados depois de liquidado: um boot manual futuro não reexecuta nada."""
        self._metadados(self._pedir("GET"), **{"infinito-job": None})
