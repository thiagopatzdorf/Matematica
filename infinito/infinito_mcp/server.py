"""∞ Infinito: o MCP universal. A matemática é o primeiro módulo; o próximo é só outro arquivo.

Núcleo (este arquivo) faz o que todo módulo precisaria refazer:

* **porta**: URL com token por pessoa, `/mcp/<token>/` (tokens.py), como o MCP da Factory; ou, com
  `INF_AUTH=access`, o JWT do Cloudflare Access (auth.py);
* **identidade**: `quem()` em qualquer tool, e auditoria JSON por chamada em stdout
  (`jsonPayload.auditoria="infinito-mcp"` no Cloud Logging);
* **dinheiro**: o ledger de créditos (creditos.py) e as tools de administração, que só
  administrador chama (é por elas que a MCP interna da Factory aumenta o crédito de alguém).

Módulo é qualquer objeto em `infinito_mcp/modulos/` com `NOME` e `registrar(ctx)`, e é ligado
por `INF_MODULOS` (padrão: `matematica,papers,pesado`). Um módulo declara tools com
`@ctx.tool`; se a tool gasta dinheiro, passa pelo `ctx.creditos` e nunca por conta própria.
"""
from __future__ import annotations

import contextvars
import functools
import importlib
import inspect
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

from .armazem import Armazem, ArmazemGCS
from .auth import CABECALHO, Config, Identidade, VerificadorAccess, configurar
from .creditos import Creditos, ErroCreditos
from .tokens import Tokens

_quem: contextvars.ContextVar[Identidade | None] = contextvars.ContextVar("inf_quem", default=None)
AUDITORIA = "infinito-mcp"
MODULOS_PADRAO = "matematica,papers,pesado,gemini"


class PortaDoAccess:
    """ASGI: nada chega ao MCP sem o JWT do Access válido (fecha o *.run.app público)."""

    def __init__(self, app, verificador: VerificadorAccess):
        self.app = app
        self.verificador = verificador

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        cab = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        ident = self.verificador.decidir(cab.get(CABECALHO))
        if ident is None:
            print(json.dumps({"severity": "WARNING", "auditoria": AUDITORIA, "recusado": True,
                              "message": "pedido sem JWT do Access válido", "caminho": scope.get("path"),
                              "tinha_jwt": CABECALHO in cab}), flush=True)
            return await JSONResponse({"erro": "acesso negado"}, status_code=403)(scope, receive, send)
        marca = _quem.set(ident)
        try:
            await self.app(scope, receive, send)
        finally:
            _quem.reset(marca)


class PortaPorToken:
    """ASGI: `/mcp/<token>/...` -> identidade da pessoa; o caminho vira `/mcp` para o servidor MCP.

    Token errado, revogado ou ausente volta 404 genérico (não revela que o caminho existe).
    """

    def __init__(self, app, tokens: Tokens):
        self.app, self.tokens = app, tokens

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        partes = scope["path"].split("/", 3)          # ['', 'mcp', '<token>', 'resto']
        ident = self.tokens.decidir(partes[2]) if len(partes) > 2 and partes[1] == "mcp" else None
        if ident is None:
            # o caminho NÃO vai para o log: ele carrega o token
            print(json.dumps({"severity": "WARNING", "auditoria": AUDITORIA, "recusado": True,
                              "message": "token ausente, errado ou revogado"}), flush=True)
            return await JSONResponse({"detail": "Not Found"}, status_code=404)(scope, receive, send)
        scope = dict(scope, path="/mcp", raw_path=b"/mcp")
        marca = _quem.set(ident)
        try:
            await self.app(scope, receive, send)
        finally:
            _quem.reset(marca)


def quem() -> str:
    ident = _quem.get()
    return ident.quem if ident else "desconhecido"


def auditar(tool: str, argumentos: dict, resultado: Any, inicio: float, saida=None) -> None:
    r = resultado if isinstance(resultado, dict) else {}
    args = {k: (str(v)[:200] if isinstance(v, str) else v) for k, v in argumentos.items()}
    linha = {"severity": "NOTICE", "auditoria": AUDITORIA, "message": f"{quem()} chamou {tool}", "quem": quem(),
             "tool": tool, "argumentos": args, "ok": r.get("ok"), "seco": bool(r.get("seco")), "erro": r.get("erro"),
             "duracao_ms": round((time.monotonic() - inicio) * 1000)}
    print(json.dumps(linha, ensure_ascii=False, default=str), file=saida or sys.stdout, flush=True)


@dataclass
class Contexto:
    """O que um módulo recebe: nada global, tudo injetável (os testes trocam armazém e rede)."""
    mcp: FastMCP
    creditos: Creditos
    estado: Armazem          # ledger, histórico de trabalho
    literatura: Armazem      # bucket de papers
    env: dict
    tokens: Tokens | None = None
    tool: Callable[..., Any] = None  # type: ignore[assignment]  # preenchido por criar_mcp

    quem = staticmethod(quem)


def _auditado(fn, creditos: Creditos):
    assinatura = inspect.signature(fn)

    @functools.wraps(fn)
    def embrulho(*args, **kwargs):
        inicio = time.monotonic()
        argumentos = dict(assinatura.bind(*args, **kwargs).arguments)
        try:
            creditos.garantir(quem())          # a 11ª pessoa para aqui, antes de qualquer tool
            resultado = fn(*args, **kwargs)
        except ErroCreditos as e:
            resultado = {"ok": False, "erro": str(e)}
        except Exception as exc:  # noqa: BLE001
            auditar(fn.__name__, argumentos, {"ok": False, "erro": type(exc).__name__}, inicio)
            raise
        auditar(fn.__name__, argumentos, resultado, inicio)
        return resultado
    return embrulho


def _tools_do_nucleo(ctx: Contexto) -> None:
    tool, creditos = ctx.tool, ctx.creditos

    @tool
    def meus_creditos() -> dict:
        """Seu teto, o que já gastou, o que está reservado e o que ainda pode gastar (US$)."""
        return {"ok": True, **creditos.saldo(quem())}

    @tool
    def admin_usuarios() -> dict:
        """[admin] Todas as pessoas, com teto, gasto e disponível. Também mostra quantas vagas restam."""
        lista = creditos.listar(quem())
        return {"ok": True, "pessoas": lista, "vagas": creditos.max_usuarios - len(lista), "maximo": creditos.max_usuarios}

    @tool
    def admin_creditos(email: str, teto_usd: float | None = None, somar_usd: float | None = None,
                       ativo: bool | None = None, motivo: str = "") -> dict:
        """[admin] Define (`teto_usd`) ou aumenta (`somar_usd`) o crédito de infra de alguém, ou liga/desliga
        (`ativo`). Motivo obrigatório; cada mudança deixa um evento no ledger."""
        return {"ok": True, **creditos.definir(quem(), email, teto_usd=teto_usd, somar_usd=somar_usd,
                                               ativo=ativo, motivo=motivo)}


def _tools_de_acesso(ctx: Contexto) -> None:
    """[admin] Convidar e revogar. O token em claro sai UMA vez, na resposta de `admin_convidar`."""
    tool, creditos, tokens = ctx.tool, ctx.creditos, ctx.tokens
    base = ctx.env.get("INF_URL_BASE", "").rstrip("/")

    @tool
    def admin_convidar(nome: str, email: str, teto_usd: float | None = None) -> dict:
        """[admin] Abre uma vaga e gera a URL pessoal (`.../mcp/<token>/`) da pessoa, com o teto de crédito
        (padrão US$ 20). A URL é a senha dela: mande por canal privado e nunca cole em chat, issue ou PR.
        O token só aparece nesta resposta; se perder, convide de novo e revogue o antigo."""
        creditos.exigir_admin(quem())
        antes = {p["quem"] for p in creditos.listar(quem())}
        creditos.definir(quem(), email, teto_usd=teto_usd if teto_usd is not None else creditos.teto_padrao,
                         motivo="convite")                       # recusa "lotado" ANTES de emitir token
        token = tokens.emitir(nome, email)
        return {"ok": True, "nome": nome, "email": email.lower(), "nova_vaga": email.lower() not in antes,
                "url": f"{base}/mcp/{token}/" if base else f"<INF_URL_BASE>/mcp/{token}/"}

    @tool
    def admin_revogar(email: str) -> dict:
        """[admin] Corta o acesso da pessoa (todos os tokens dela) e desativa o crédito. Não apaga histórico."""
        creditos.exigir_admin(quem())
        n = tokens.revogar(email)
        creditos.definir(quem(), email, ativo=False, motivo="revogado")
        return {"ok": True, "tokens_revogados": n}

    @tool
    def admin_acessos() -> dict:
        """[admin] Quem tem token (sem o token), se está ativo e quando foi criado."""
        creditos.exigir_admin(quem())
        return {"ok": True, "acessos": tokens.listar()}


def criar_mcp(creditos: Creditos, estado: Armazem, literatura: Armazem, env: dict | None = None,
              modulos: list[str] | None = None, tokens: Tokens | None = None) -> FastMCP:
    env = dict(os.environ if env is None else env)
    mcp = FastMCP(
        "Infinito",
        instructions=(
            "∞ Infinito: ferramentas de pesquisa com orçamento. Comece por `meus_creditos`. O que custa dinheiro "
            "é sempre seco por padrão (mostra o preço e o saldo) e só roda com confirmar=true; o teto é por pessoa "
            "e é aplicado em código. Módulo de matemática: ledger de cotas de códigos de cobertura, certificados do "
            "Lean, verificador oficial. Módulo de papers: arXiv, OpenAlex, Semantic Scholar, Zenodo e a biblioteca. "
            "Publicar (Zenodo, site) e fazer merge não existem aqui: são do dono."
        ),
        host="0.0.0.0", stateless_http=True, json_response=True,
    )
    ctx = Contexto(mcp=mcp, creditos=creditos, estado=estado, literatura=literatura, env=env, tokens=tokens)
    ctx.tool = lambda fn: mcp.tool()(_auditado(fn, creditos))
    _tools_do_nucleo(ctx)
    if tokens is not None:
        _tools_de_acesso(ctx)
    for nome in (modulos if modulos is not None else env.get("INF_MODULOS", MODULOS_PADRAO).split(",")):
        nome = nome.strip()
        if nome:
            importlib.import_module(f"{__package__}.modulos.{nome}").registrar(ctx)
    return mcp


def app(cfg: Config | None = None, *, estado: Armazem | None = None, literatura: Armazem | None = None,
        verificador: VerificadorAccess | None = None, env: dict | None = None, modulos: list[str] | None = None):
    env = dict(os.environ if env is None else env)
    estado = estado or ArmazemGCS(env.get("INF_BUCKET_ESTADO", "infinito-mcp-estado"))
    literatura = literatura or ArmazemGCS(env.get("INF_BUCKET_LITERATURA", "factory-literatura-matematica"))
    admins = frozenset(a.strip().lower() for a in env.get("INF_ADMINS", "").split(",") if a.strip())
    creditos = Creditos(estado, admins=admins, max_usuarios=int(env.get("INF_MAX_USUARIOS", "10")),
                        teto_padrao_usd=float(env.get("INF_TETO_PADRAO_USD", "20")))
    if cfg is None:     # padrão: URL com token por pessoa (o jeito que a Factory já usa)
        tokens = Tokens(estado, token_admin=env.get("INF_TOKEN_ADMIN") or None)
        return PortaPorToken(criar_mcp(creditos, estado, literatura, env, modulos, tokens).streamable_http_app(), tokens)
    return PortaDoAccess(criar_mcp(creditos, estado, literatura, env, modulos).streamable_http_app(),
                         verificador or VerificadorAccess(cfg))


def main() -> None:
    import uvicorn
    env = dict(os.environ)
    uvicorn.run(app(configurar(env) if env.get("INF_AUTH") == "access" else None, env=env), host=env.get("INF_HOST", "0.0.0.0"), port=int(env.get("PORT", "8080")))


if __name__ == "__main__":
    main()
