"""Quem está chamando? O Cloudflare Access responde; o servidor confere de novo.

Mesmo desenho do propostas-mcp (apps/propostas/mcp/propostas_mcp/auth.py, fabrica-de-sites):
o Access é o servidor OAuth do MCP (PIN no e-mail, política com a lista de convidados) e o
Cloud Run só aceita pedido com `Cf-Access-Jwt-Assertion` válido (RS256, `aud`, `iss`).

Diferença daqui: `INF_EMAILS` é opcional. Quem convida é a política do Access; quem gasta é o
ledger de créditos (creditos.py), que limita a quantidade de pessoas e o dinheiro de cada uma.
Se `INF_EMAILS` vier preenchida, vira segunda trava (política editada por engano no painel não
abre a nuvem). Token de serviço do Access (a MCP interna da Factory) não tem e-mail: entra como
administrador se o client id estiver em `INF_TOKENS_SERVICO`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import jwt

CABECALHO = "cf-access-jwt-assertion"


@dataclass(frozen=True)
class Config:
    equipe: str                          # ex.: mybagcenter.cloudflareaccess.com
    aud: str                             # tag AUD da aplicação Access
    emails: frozenset[str]
    tokens_servico: frozenset[str] = frozenset()   # client ids aceitos (prova/automação)

    @property
    def emissor(self) -> str:
        return f"https://{self.equipe}"

    @property
    def certs(self) -> str:
        return f"https://{self.equipe}/cdn-cgi/access/certs"


def _lista(valor: str | None) -> frozenset[str]:
    return frozenset(v.strip().lower() for v in (valor or "").split(",") if v.strip())


def configurar(env: dict) -> Config:
    """Não existe modo aberto: falta de qualquer peça impede o servidor de subir."""
    equipe = (env.get("INF_ACCESS_EQUIPE") or "").strip().removeprefix("https://").rstrip("/")
    aud = (env.get("INF_ACCESS_AUD") or "").strip()
    emails = _lista(env.get("INF_EMAILS"))
    if not equipe.endswith(".cloudflareaccess.com"):
        raise ValueError("INF_ACCESS_EQUIPE tem de ser <time>.cloudflareaccess.com")
    if not aud:
        raise ValueError("INF_ACCESS_AUD vazio: JWT de qualquer app do time passaria")
    return Config(equipe=equipe, aud=aud, emails=emails, tokens_servico=_lista(env.get("INF_TOKENS_SERVICO")))


@dataclass(frozen=True)
class Identidade:
    quem: str        # e-mail, ou "servico:<client id>"
    tipo: str        # "email" | "servico"


ChaveDoJwt = Callable[[str], Any]


class VerificadorAccess:
    """Confere o JWT do Access. `chave_do_jwt` é injetável para os testes."""

    def __init__(self, cfg: Config, chave_do_jwt: ChaveDoJwt | None = None):
        self.cfg = cfg
        if chave_do_jwt is None:
            # PyJWKClient guarda as chaves em cache e rebusca quando aparece
            # um `kid` novo (o Access gira as chaves).
            cliente = jwt.PyJWKClient(cfg.certs, cache_keys=True, lifespan=3600, timeout=8)
            chave_do_jwt = lambda t: cliente.get_signing_key_from_jwt(t).key  # noqa: E731
        self._chave = chave_do_jwt

    def decidir(self, token: str | None) -> Identidade | None:
        if not token:
            return None
        try:
            chave = self._chave(token)
            claims = jwt.decode(
                token, chave, algorithms=["RS256"], audience=self.cfg.aud, issuer=self.cfg.emissor,
                options={"require": ["exp", "iat", "aud", "iss"]}, leeway=30,
            )
        except Exception:  # noqa: BLE001 - assinatura, aud, iss, exp, rede: tudo é "não"
            return None
        email = str(claims.get("email") or "").lower()
        if email:
            return Identidade(email, "email") if (not self.cfg.emails or email in self.cfg.emails) else None
        cn = str(claims.get("common_name") or "").lower()
        if cn and cn in self.cfg.tokens_servico:
            return Identidade(f"servico:{cn}", "servico")
        return None
