"""∞ Infinito. Cada nome descreve a falha que o teste impede.

    pip install -r infinito/requirements.txt pytest httpx
    pytest infinito/tests
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.testclient import TestClient

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))

from infinito_mcp import server  # noqa: E402
from infinito_mcp.armazem import ArmazemMemoria  # noqa: E402
from infinito_mcp.auth import Config, VerificadorAccess  # noqa: E402
from infinito_mcp.creditos import Creditos, ErroCreditos  # noqa: E402
from infinito_mcp.modulos import matematica, papers, pesado  # noqa: E402

EQUIPE = "time-teste.cloudflareaccess.com"
AUD = "aud-do-infinito"
CHAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
DONO = "dono@exemplo.com"
REPO = AQUI.parent


def creditos(armazem=None, **kw):
    return Creditos(armazem or ArmazemMemoria(), admins=frozenset({DONO}), **kw)


# ------------------------------------------------------------------ créditos
def test_pessoa_onze_gasta_em_vez_de_receber_lotado():
    c = creditos(max_usuarios=10)
    for i in range(10):
        c.garantir(f"p{i}@x.com")
    with pytest.raises(ErroCreditos, match="lotado"):
        c.garantir("p10@x.com")


def test_admin_ocupa_vaga_e_atrapalha_as_dez_pessoas():
    c = creditos(max_usuarios=2)
    c.garantir(DONO)
    c.garantir("a@x.com")
    c.garantir("b@x.com")  # o dono não pode ter tomado uma das duas vagas


def test_teto_padrao_e_vinte_dolares():
    assert creditos().saldo("a@x.com")["disponivel_usd"] == 20.0


def test_duas_reservas_juntas_furam_o_teto():
    c = creditos()
    c.reservar("a@x.com", "t", 12.0)
    with pytest.raises(ErroCreditos, match="insuficiente"):
        c.reservar("a@x.com", "t", 12.0)  # reserva aberta já conta como gasto


def test_cancelar_devolve_o_credito_e_confirmar_cobra_o_real():
    c = creditos()
    r1 = c.reservar("a@x.com", "t", 5.0)
    c.cancelar("a@x.com", r1)
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0
    r2 = c.reservar("a@x.com", "t", 5.0)
    c.confirmar("a@x.com", r2, 3.0)
    s = c.saldo("a@x.com")
    assert (s["gasto_usd"], s["reservado_usd"], s["disponivel_usd"]) == (3.0, 0.0, 17.0)


def test_ledger_fora_do_ar_deixa_gastar_sem_medir():
    class Quebrado(ArmazemMemoria):
        def ler(self, nome):
            raise OSError("bucket fora")

    with pytest.raises(ErroCreditos, match="sem ledger"):
        creditos(Quebrado()).reservar("a@x.com", "t", 0.01)


def test_colaborador_aumenta_o_proprio_credito():
    c = creditos()
    with pytest.raises(ErroCreditos, match="só administrador"):
        c.definir("a@x.com", "a@x.com", somar_usd=100, motivo="eu quero")


def test_servico_da_factory_e_admin_e_aumenta_credito_com_motivo():
    c = creditos()
    r = c.definir("servico:abc.access", "a@x.com", somar_usd=10, motivo="rodada de busca K7(9,4)")
    assert r["teto_usd"] == 30.0
    with pytest.raises(ErroCreditos, match="motivo"):
        c.definir(DONO, "a@x.com", somar_usd=1, motivo=" ")
    with pytest.raises(ErroCreditos, match="ambíguos"):
        c.definir(DONO, "a@x.com", teto_usd=5, somar_usd=1, motivo="m")


def test_pessoa_desativada_continua_gastando():
    c = creditos()
    assert c.definir(DONO, "a@x.com", ativo=False, motivo="saiu do projeto")["ativo"] is False
    assert [p["ativo"] for p in c.listar(DONO)] == [False]
    with pytest.raises(ErroCreditos, match="desativado"):
        c.saldo("a@x.com")


# ---------------------------------------------------------------- matemática
def test_celula_com_formatos_ambiguos_vira_outra_celula():
    assert matematica.parse_celula("K7(9,4)") == "K7(9,4)"
    assert matematica.parse_celula("7, 9, 4") == "K7(9,4)"
    with pytest.raises(ValueError):
        matematica.parse_celula("79,4")


class _Ctx:
    """Contexto mínimo: o decorador devolve a função crua, para chamar direto."""

    def __init__(self, c, lit=None, env=None):
        self.creditos, self.literatura, self.env = c, lit or ArmazemMemoria(), env or {"INF_REPO": str(REPO)}
        self.tools = {}
        self.tool = self._tool
        self.quem = lambda: "a@x.com"

    def _tool(self, fn):
        self.tools[fn.__name__] = fn
        return fn


def test_ledger_do_repo_tem_a_celula_que_batemos():
    ctx = _Ctx(creditos())
    matematica.registrar(ctx)
    r = ctx.tools["celula"]("K7(9,4)")
    assert r["ok"] and r["celula"]["best"]["ub"] == 1137
    assert ctx.tools["celula"]("K99(9,4)")["ok"] is False
    assert ctx.tools["alvos"](limite=3)["alvos"][0]["rank"] == 1


def test_verificador_aceita_caminho_fora_de_data_codes():
    ctx = _Ctx(creditos())
    matematica.registrar(ctx)
    for ruim in ("../../etc/passwd", "q5_n7_R2_M500.txt/../../x", "/etc/passwd", "q5_n7_R2_M500.json"):
        assert ctx.tools["verificar_codigo"](ruim)["ok"] is False


def test_documento_fora_da_lista_le_arquivo_qualquer():
    ctx = _Ctx(creditos())
    matematica.registrar(ctx)
    assert ctx.tools["documento"]("../.git/config")["ok"] is False
    assert ctx.tools["documento"]("estado_da_arte")["texto"].startswith("# Estado da arte")


# -------------------------------------------------------------------- papers
def test_mesma_busca_de_outra_pessoa_bate_de_novo_na_fonte():
    chamadas = []
    ctx = _Ctx(creditos())
    papers.registrar(ctx, {"arxiv": lambda q, n: chamadas.append(q) or [{"titulo": "T"}]})
    a = ctx.tools["papers_buscar"]("covering codes")
    b = ctx.tools["papers_buscar"]("Covering Codes ")
    assert (a["cache"], b["cache"], len(chamadas)) == (False, True, 1)


def test_fonte_fora_do_ar_derruba_o_servidor():
    def cai(q, n):
        raise TimeoutError

    ctx = _Ctx(creditos())
    papers.registrar(ctx, {"arxiv": cai})
    assert ctx.tools["papers_buscar"]("x")["ok"] is False


def test_pdf_de_host_interno_ou_http_vira_proxy_aberto():
    ctx = _Ctx(creditos())
    papers.registrar(ctx, {}, baixar=lambda u: b"%PDF-x")
    for url in ("http://arxiv.org/pdf/1", "https://metadata.google.internal/x", "https://arxiv.org.evil.com/a.pdf"):
        assert ctx.tools["paper_guardar"](url, "t", confirmar=True)["ok"] is False


def test_guardar_paper_nao_pdf_ou_duplicado():
    ctx = _Ctx(creditos())
    papers.registrar(ctx, {}, baixar=lambda u: b"%PDF-1.7 conteudo")
    url = "https://arxiv.org/pdf/2608.19872v3"
    assert ctx.tools["paper_guardar"](url, "Marosi")["seco"] is True
    assert ctx.literatura.listar("pdf/") == []
    assert ctx.tools["paper_guardar"](url, "Marosi", confirmar=True)["ja_existia"] is False
    assert ctx.tools["paper_guardar"](url, "Marosi", confirmar=True)["ja_existia"] is True
    assert ctx.tools["biblioteca_buscar"]("marosi")["total"] == 1
    papers.registrar(ctx2 := _Ctx(creditos()), {}, baixar=lambda u: b"<html>")
    assert ctx2.tools["paper_guardar"](url, "x", confirmar=True)["ok"] is False


# -------------------------------------------------------------------- pesado
def test_pesado_sem_executor_cobra_e_finge_que_rodou():
    c = creditos()
    ctx = _Ctx(c)
    pesado.registrar(ctx)
    seco = ctx.tools["pesado"]("lake_build", 1.0)
    assert seco["seco"] and seco["custo_estimado_usd"] == 0.6 and seco["cabe"]
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    assert r["ok"] is False and "nenhum executor" in r["erro"]
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0  # reserva desfeita


def test_pesado_com_executor_deixa_a_reserva_aberta_e_respeita_o_teto():
    class Ex:
        def iniciar(self, tipo, parametros, horas, quem):
            return {"id": "job1"}

    c = creditos()
    ctx = _Ctx(c)
    pesado.registrar(ctx, Ex())
    assert ctx.tools["pesado"]("lake_build", 3.0, confirmar=True)["job"] == {"id": "job1"}
    assert c.saldo("a@x.com")["reservado_usd"] == 1.8
    assert ctx.tools["pesado"]("comando_livre", 1.0, confirmar=True)["ok"] is False
    assert ctx.tools["pesado"]("lake_build", 99.0, confirmar=True)["ok"] is False
    for _ in range(40):
        try:
            ctx.tools["pesado"]("lake_build", 3.0, confirmar=True)
        except ErroCreditos:
            break
    assert c.saldo("a@x.com")["disponivel_usd"] >= 0


# ------------------------------------------------------------- HTTP + Access
def _jwt(**extra):
    agora = int(time.time())
    c = {"iss": f"https://{EQUIPE}", "aud": [AUD], "email": "a@x.com", "iat": agora, "exp": agora + 300}
    c.update(extra)
    return jwt.encode({k: v for k, v in c.items() if v is not None}, CHAVE, algorithm="RS256", headers={"kid": "k"})


def _cliente(estado):
    cfg = Config(equipe=EQUIPE, aud=AUD, emails=frozenset())
    asgi = server.app(cfg, estado=estado, literatura=ArmazemMemoria(), env={"INF_REPO": str(REPO), "INF_ADMINS": DONO},
                      verificador=VerificadorAccess(cfg, chave_do_jwt=lambda t: CHAVE.public_key()))
    return TestClient(asgi, base_url="https://infinito-teste.run.app")


def _rpc(c, metodo, params, token=None, id_=1):
    cab = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    if token:
        cab["Cf-Access-Jwt-Assertion"] = token
    return c.post("/mcp", headers=cab, json={"jsonrpc": "2.0", "id": id_, "method": metodo, "params": params})


def _tool(c, nome, args, token=None):
    return _rpc(c, "tools/call", {"name": nome, "arguments": args}, token)


def _dado(r):
    return json.loads(r.json()["result"]["content"][0]["text"])


def test_run_app_direto_sem_jwt_gasta_credito_de_alguem():
    est = ArmazemMemoria()
    with _cliente(est) as c:
        assert _tool(c, "meus_creditos", {}).status_code == 403
        assert _tool(c, "meus_creditos", {}, "lixo").status_code == 403
    assert est.objs == {}


def test_tools_do_servidor_e_colaborador_chamando_admin(capsys):
    est = ArmazemMemoria()
    with _cliente(est) as c:
        nomes = {t["name"] for t in _rpc(c, "tools/list", {}, _jwt()).json()["result"]["tools"]}
        assert {"meus_creditos", "admin_creditos", "celula", "alvos", "papers_buscar", "pesado"} <= nomes
        assert _dado(_tool(c, "meus_creditos", {}, _jwt()))["disponivel_usd"] == 20.0
        negado = _dado(_tool(c, "admin_creditos", {"email": "a@x.com", "somar_usd": 500, "motivo": "x"}, _jwt()))
        assert negado["ok"] is False
        ok = _dado(_tool(c, "admin_creditos", {"email": "a@x.com", "somar_usd": 10, "motivo": "rodada"}, _jwt(email=DONO)))
        assert ok["teto_usd"] == 30.0
    linhas = [json.loads(l) for l in capsys.readouterr().out.splitlines() if '"tool"' in l]
    assert any(l["quem"] == DONO and l["tool"] == "admin_creditos" for l in linhas)
