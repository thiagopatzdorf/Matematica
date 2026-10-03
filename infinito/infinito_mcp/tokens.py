"""Acesso por URL com token: `https://<host>/mcp/<token>/`, um token por pessoa.

Mesmo padrão do MCP da Factory (e dos acessos que o Thiago já mandou por e-mail): o conector
personalizado do claude.ai não manda cabeçalho fixo, então a credencial vai no caminho. A URL
inteira é a senha de quem a recebeu.

O que impede isso de ser uma senha compartilhada:

* **um token por pessoa**, com nome e e-mail: toda chamada e todo gasto saem com a identidade dela,
  e cortar uma pessoa (`revogar`) não afeta as outras;
* **só o hash (sha256) fica guardado**: o token em claro existe uma vez, na resposta de `emitir`,
  e nunca mais. Perdeu? Emite outro e revoga o velho;
* comparação em tempo constante, e token errado volta 404 (não 401/403), sem dizer que o caminho existe;
* o token do administrador (a MCP interna da Factory) vem do ambiente (`INF_TOKEN_ADMIN`, do cofre),
  nunca do ledger.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from typing import Callable

from .armazem import Armazem
from .auth import Identidade

ARQUIVO = "acesso/tokens.json"


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Tokens:
    def __init__(self, armazem: Armazem, token_admin: str | None = None, relogio: Callable[[], float] = time.time):
        self.armazem = armazem
        self._admin = _hash(token_admin) if token_admin else None
        self._agora = relogio

    def _ler(self) -> dict:
        bruto = self.armazem.ler(ARQUIVO)
        return json.loads(bruto)["tokens"] if bruto else {}

    def _gravar(self, tokens: dict) -> None:
        self.armazem.por(ARQUIVO, json.dumps({"tokens": tokens}, ensure_ascii=False, indent=1).encode(),
                         "application/json", publico=False)

    def emitir(self, nome: str, email: str) -> str:
        """Devolve o token em claro. É a única vez que ele existe."""
        if not nome.strip() or "@" not in email:
            raise ValueError("nome e e-mail são obrigatórios")
        token = secrets.token_urlsafe(32)
        tokens = self._ler()
        tokens[_hash(token)] = {"nome": nome.strip(), "email": email.strip().lower(), "ativo": True, "criado": self._agora()}
        self._gravar(tokens)
        return token

    def revogar(self, email: str) -> int:
        tokens, n = self._ler(), 0
        for t in tokens.values():
            if t["email"] == email.strip().lower() and t["ativo"]:
                t["ativo"], n = False, n + 1
        if n:
            self._gravar(tokens)
        return n

    def listar(self) -> list[dict]:
        return sorted(({"nome": t["nome"], "email": t["email"], "ativo": t["ativo"], "criado": t["criado"]}
                       for t in self._ler().values()), key=lambda t: t["email"])

    def decidir(self, token: str | None) -> Identidade | None:
        if not token:
            return None
        h = _hash(token)
        if self._admin and hmac.compare_digest(h, self._admin):
            return Identidade("servico:factory", "servico")
        try:
            t = self._ler().get(h)
        except Exception:  # noqa: BLE001 - sem ledger de tokens, ninguém entra
            return None
        return Identidade(t["email"], "email") if t and t["ativo"] else None
