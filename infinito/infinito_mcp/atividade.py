"""Quem está usando: um resumo por pessoa, barato de consultar.

O pedido do Thiago (2026-10-03): os nomes ficam `colaborador-NN`, mas "precisamos saber quem tá usando de uma
consulta fácil". A resposta é `admin_usuarios`: cada pessoa com nome, chamadas, última atividade, tools mais usadas
e saldo, ordenada por quem usou há menos tempo.

Um único objeto (`atividade/resumo.json`) em vez de um evento por chamada: ler o resumo é uma leitura, e o serviço
roda com no máximo uma instância, então o trinco em processo basta. **Registrar nunca derruba uma tool**: se o
armazém falha, a chamada segue e a atividade daquela chamada se perde (o log de auditoria no stdout continua).
"""
from __future__ import annotations

import json
import threading
import time
from typing import Callable

from .armazem import Armazem

ARQUIVO = "atividade/resumo.json"


class Atividade:
    def __init__(self, armazem: Armazem, relogio: Callable[[], float] = time.time):
        self.armazem, self._agora, self._trava = armazem, relogio, threading.Lock()

    def _ler(self) -> dict:
        bruto = self.armazem.ler(ARQUIVO)
        return json.loads(bruto) if bruto else {}

    def registrar(self, quem: str, tool: str) -> None:
        try:
            with self._trava:
                resumo, agora = self._ler(), self._agora()
                p = resumo.setdefault(quem, {"chamadas": 0, "primeira": agora, "tools": {}})
                p["chamadas"] += 1
                p["ultima"] = agora
                p["tools"][tool] = p["tools"].get(tool, 0) + 1
                self.armazem.por(ARQUIVO, json.dumps(resumo, ensure_ascii=False).encode(), "application/json", publico=False)
        except Exception:  # noqa: BLE001 - atividade é informação, nunca um motivo para a tool falhar
            pass

    def resumo(self) -> dict:
        try:
            return self._ler()
        except Exception:  # noqa: BLE001
            return {}


def iso(ts: float | None) -> str | None:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)) if ts else None
