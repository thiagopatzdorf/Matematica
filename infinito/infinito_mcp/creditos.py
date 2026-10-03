"""Créditos de infra por pessoa: o teto é código, não promessa.

Pedido do Thiago (2026-10-03): até 10 pessoas, cada uma com US$ 20 de infra, e ele aumenta
o crédito pela MCP interna da Factory. Por isso:

* `INF_MAX_USUARIOS` (padrão 10) limita quantas pessoas entram. A 11ª recebe "lotado" e não
  gasta nada. Subir o número é uma variável de ambiente, não um deploy de código.
* O teto de cada pessoa mora no ledger (`usuarios.json`), não no código. Quem muda é a tool
  `admin_creditos`, que só administrador (e-mail em `INF_ADMINS` ou token de serviço) chama.
* Gasto é reserva antes, confirmação depois (mesmo desenho do ledger `GeminiUso` da loja): uma
  reserva aberta já conta como gasto, então duas chamadas em paralelo não furam o teto.
* **Sem ledger, bloqueia.** Se o armazém não responde, nada que custa dinheiro roda.

Um evento por objeto (`creditos/eventos/<pessoa>/<ts>-<id>-<tipo>.json`): escrever nunca
sobrescreve histórico, e o saldo é sempre recalculado dos eventos (nada de contador que desvia).
"""
from __future__ import annotations

import json
import re
import threading
import time
import uuid
from typing import Callable

from .armazem import Armazem

USUARIOS = "creditos/usuarios.json"
EVENTOS = "creditos/eventos/"


class ErroCreditos(Exception):
    """Recusa com motivo legível. Volta ao agente como dado, não como exceção de servidor."""


def _chave(email: str) -> str:
    return re.sub(r"[^a-z0-9@._-]", "_", email.strip().lower())


class Creditos:
    def __init__(self, armazem: Armazem, *, admins: frozenset[str] = frozenset(), max_usuarios: int = 10,
                 teto_padrao_usd: float = 20.0, relogio: Callable[[], float] = time.time):
        self.armazem = armazem
        self.admins = frozenset(a.lower() for a in admins)
        self.max_usuarios = max_usuarios
        self.teto_padrao = float(teto_padrao_usd)
        self._agora = relogio
        self._trava = threading.RLock()

    # ------------------------------------------------------------- usuários
    def _ler_usuarios(self) -> dict:
        try:
            bruto = self.armazem.ler(USUARIOS)
        except Exception as e:  # noqa: BLE001 - qualquer falha do armazém é "sem ledger"
            raise ErroCreditos(f"sem ledger de créditos ({type(e).__name__}): nada que custa dinheiro roda") from e
        return json.loads(bruto)["usuarios"] if bruto else {}

    def _gravar_usuarios(self, usuarios: dict) -> None:
        self.armazem.por(USUARIOS, json.dumps({"usuarios": usuarios}, ensure_ascii=False, indent=1).encode(),
                         "application/json", publico=False)

    def e_admin(self, quem: str) -> bool:
        return quem.startswith("servico:") or quem.lower() in self.admins

    def garantir(self, quem: str) -> dict:
        """Registra a pessoa na primeira chamada, até `max_usuarios`. Administrador não ocupa vaga."""
        if self.e_admin(quem):
            return {"teto_usd": None, "ativo": True, "admin": True}
        with self._trava:
            usuarios = self._ler_usuarios()
            u = usuarios.get(quem.lower())
            if u is None:
                if len(usuarios) >= self.max_usuarios:
                    raise ErroCreditos(f"lotado: já são {self.max_usuarios} pessoas. Peça ao administrador para abrir vaga")
                u = {"teto_usd": self.teto_padrao, "ativo": True, "criado": self._agora()}
                usuarios[quem.lower()] = u
                self._gravar_usuarios(usuarios)
            if not u.get("ativo", True):
                raise ErroCreditos("acesso desativado pelo administrador")
            return u

    # --------------------------------------------------------------- saldo
    def _eventos(self, quem: str) -> list[dict]:
        nomes = self.armazem.listar(f"{EVENTOS}{_chave(quem)}/")
        return [json.loads(self.armazem.ler(n)) for n in nomes]

    def saldo(self, quem: str) -> dict:
        return self._saldo_de(quem, self.garantir(quem))

    def _saldo_de(self, quem: str, u: dict) -> dict:
        """Saldo sem checar `ativo`: o administrador precisa ver (e devolver) quem está desativado."""
        gasto, abertas, fechadas = 0.0, {}, set()
        for e in sorted(self._eventos(quem), key=lambda e: e["ts"]):
            if e["tipo"] == "reserva":
                abertas[e["id"]] = e["usd"]
            elif e["tipo"] == "confirmacao":
                abertas.pop(e["id"], None)
                fechadas.add(e["id"])
                gasto += e["usd"]
            elif e["tipo"] == "cancelamento":
                abertas.pop(e["id"], None)
        reservado = sum(abertas.values())
        teto = u["teto_usd"]
        return {"quem": quem, "teto_usd": teto, "gasto_usd": round(gasto, 6), "reservado_usd": round(reservado, 6),
                "disponivel_usd": None if teto is None else round(teto - gasto - reservado, 6), "admin": bool(u.get("admin"))}

    def _evento(self, quem: str, tipo: str, id_: str, usd: float, **extra) -> None:
        ts = self._agora()
        corpo = {"ts": ts, "tipo": tipo, "id": id_, "usd": round(usd, 6), "quem": quem, **extra}
        nome = f"{EVENTOS}{_chave(quem)}/{int(ts * 1e6):020d}-{id_}-{tipo}.json"
        self.armazem.por(nome, json.dumps(corpo, ensure_ascii=False).encode(), "application/json", publico=False)

    # ------------------------------------------------------- reserva e fecho
    def reservar(self, quem: str, tool: str, usd: float) -> str:
        if usd < 0:
            raise ErroCreditos("custo negativo")
        with self._trava:
            s = self.saldo(quem)
            if s["disponivel_usd"] is not None and usd > s["disponivel_usd"] + 1e-9:
                raise ErroCreditos(f"crédito insuficiente: precisa de US$ {usd:.2f}, disponível US$ {s['disponivel_usd']:.2f}")
            id_ = uuid.uuid4().hex[:12]
            self._evento(quem, "reserva", id_, usd, tool=tool)
            return id_

    def confirmar(self, quem: str, id_: str, usd_real: float) -> None:
        self._evento(quem, "confirmacao", id_, usd_real)

    def cancelar(self, quem: str, id_: str) -> None:
        self._evento(quem, "cancelamento", id_, 0.0)

    # ------------------------------------------------------------ administração
    def exigir_admin(self, quem: str) -> None:
        if not self.e_admin(quem):
            raise ErroCreditos("só administrador")

    def definir(self, admin: str, email: str, *, teto_usd: float | None = None, somar_usd: float | None = None,
                ativo: bool | None = None, motivo: str = "") -> dict:
        """Muda o teto (absoluto ou soma), ou liga/desliga a pessoa. Cada mudança deixa um evento."""
        self.exigir_admin(admin)
        if teto_usd is not None and somar_usd is not None:
            raise ErroCreditos("teto_usd e somar_usd juntos são ambíguos: passe um")
        if teto_usd is None and somar_usd is None and ativo is None:
            raise ErroCreditos("passe teto_usd, somar_usd ou ativo")
        if not motivo.strip():
            raise ErroCreditos("motivo é obrigatório: crédito sem motivo vira folclore")
        with self._trava:
            usuarios = self._ler_usuarios()
            alvo = email.lower()
            if alvo not in usuarios and len(usuarios) >= self.max_usuarios:
                raise ErroCreditos(f"lotado: já são {self.max_usuarios} pessoas (suba INF_MAX_USUARIOS para abrir vagas)")
            u = usuarios.setdefault(alvo, {"teto_usd": self.teto_padrao, "ativo": True, "criado": self._agora()})
            antes = dict(u)
            if teto_usd is not None:
                if teto_usd < 0:
                    raise ErroCreditos("teto negativo")
                u["teto_usd"] = float(teto_usd)
            if somar_usd is not None:
                u["teto_usd"] = max(0.0, float(u["teto_usd"]) + float(somar_usd))
            if ativo is not None:
                u["ativo"] = bool(ativo)
            self._gravar_usuarios(usuarios)
            self._evento(alvo, "ajuste", uuid.uuid4().hex[:12], 0.0, por=admin, motivo=motivo.strip(),
                         antes=antes.get("teto_usd"), depois=u["teto_usd"], ativo=u["ativo"])
        return {"email": alvo, **self._saldo_de(alvo, u), "ativo": u["ativo"]}

    def listar(self, admin: str) -> list[dict]:
        self.exigir_admin(admin)
        return [self._saldo_de(e, u) | {"ativo": u.get("ativo", True)} for e, u in sorted(self._ler_usuarios().items())]
