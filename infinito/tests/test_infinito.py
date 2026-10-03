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
        self.estado = ArmazemMemoria()
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
class VMFalsa:
    """Executor de mentira com o contrato do real: um job por vez, status lido da 'VM'."""

    def __init__(self):
        self.st, self.ligada, self.liberada = {}, False, 0

    def iniciar(self, tipo, parametros, horas, quem, job_id=""):
        if self.ligada:
            raise ErroCreditos("a VM está ocupada (RUNNING)")
        self.ligada, self.job = True, job_id
        return {"vm": "ligando"}

    def status(self, job_id):
        return dict(self.st)

    def parar(self):
        self.ligada = False

    def liberar(self):
        self.liberada += 1


def _pesado(vm=None, relogio=None):
    c = creditos()
    ctx = _Ctx(c)
    pesado.registrar(ctx, vm, **({"agora": relogio} if relogio else {}))
    return ctx, c


def test_pesado_sem_executor_cobra_e_finge_que_rodou():
    ctx, c = _pesado()
    seco = ctx.tools["pesado"]("lake_build", 1.0)
    assert seco["seco"] and seco["custo_maximo_usd"] == 0.6 and seco["cabe"]
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    assert r["ok"] is False and "nenhum executor" in r["erro"]
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0  # reserva desfeita


def test_pesado_aceita_comando_livre_horas_absurdas_ou_busca_sem_executor_de_resultado():
    ctx, _ = _pesado(VMFalsa())
    assert "busca" not in pesado.TIPOS                          # a VM não devolve arquivo: busca não é um tipo
    for tipo, h in (("comando_livre", 1.0), ("lake_build", 99.0), ("lake_build", 0.0), ("lake_build", -1.0)):
        assert ctx.tools["pesado"](tipo, h, confirmar=True)["ok"] is False


def test_job_que_terminou_cobra_o_tempo_real_e_nao_a_reserva_inteira():
    vm = VMFalsa()
    ctx, c = _pesado(vm, relogio=lambda: 1000.0)
    r = ctx.tools["pesado"]("lake_build", 3.0, confirmar=True)
    assert r["ok"] and c.saldo("a@x.com")["reservado_usd"] == 1.8
    vm.st = {"vm": "TERMINATED", "inicio_vm": 1000.0, "fim_vm": 1000.0 + 1800, "estado": "concluido", "codigo": 0,
             "saida": "Build completed"}
    j = ctx.tools["pesado_status"](r["job"])["jobs"][0]
    assert (j["estado"], j["horas_reais"], j["custo_usd"], j["codigo"]) == ("liquidado", 0.5, 0.3, 0)
    s = c.saldo("a@x.com")
    assert (s["gasto_usd"], s["reservado_usd"]) == (0.3, 0.0) and vm.liberada == 1
    assert ctx.tools["pesado_status"](r["job"])["jobs"][0]["custo_usd"] == 0.3     # liquidar de novo não cobra de novo
    assert c.saldo("a@x.com")["gasto_usd"] == 0.3


def test_job_que_estourou_o_prazo_continua_ligado_e_cobrando():
    vm, t = VMFalsa(), [1000.0]
    ctx, c = _pesado(vm, relogio=lambda: t[0])
    r = ctx.tools["pesado"]("verificar_grande", 1.0, {"arquivo": "q4_n10_R4_M192.txt"}, confirmar=True)
    vm.st = {"vm": "RUNNING", "inicio_vm": 1000.0, "estado": "rodando"}
    assert ctx.tools["pesado_status"](r["job"])["jobs"][0]["estado"] == "rodando" and vm.ligada
    t[0] += 3600 + 600
    j = ctx.tools["pesado_status"](r["job"])["jobs"][0]
    assert j["estado"] == "liquidado" and j["custo_usd"] == 0.6 and not vm.ligada
    assert c.saldo("a@x.com")["gasto_usd"] == 0.6


def test_job_que_nunca_ligou_cobra_pela_reserva():
    vm = VMFalsa()
    ctx, c = _pesado(vm, relogio=lambda: 5000.0)
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    vm.st = {"vm": "TERMINATED", "inicio_vm": 10.0, "fim_vm": 20.0}      # a VM tem outra história, não a deste job
    assert ctx.tools["pesado_status"](r["job"])["jobs"][0]["estado"] == "nao_rodou"
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0


def test_job_de_outra_pessoa_aparece_na_consulta_de_quem_nao_e_dono():
    vm = VMFalsa()
    ctx, c = _pesado(vm)
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    ctx.quem = lambda: "b@x.com"
    assert ctx.tools["pesado_status"](r["job"])["ok"] is False
    assert ctx.tools["pesado_status"]()["jobs"] == []
    ctx.quem = lambda: DONO
    assert ctx.tools["pesado_status"](r["job"])["ok"] is True


def test_vm_ocupada_recusa_e_devolve_a_reserva():
    vm = VMFalsa()
    ctx, c = _pesado(vm)
    assert ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)["ok"]
    r = ctx.tools["pesado"]("lake_build", 1.0, confirmar=True)
    assert r["ok"] is False and "ocupada" in r["erro"]
    assert c.saldo("a@x.com")["reservado_usd"] == 0.6                # só o job que está rodando


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
        assert {"meus_creditos", "celula", "alvos", "papers_buscar", "pesado"} <= nomes
        assert not any(n.startswith("admin_") for n in nomes)          # colaborador não vê botão de admin
        admin = {t["name"] for t in _rpc(c, "tools/list", {}, _jwt(email=DONO)).json()["result"]["tools"]}
        assert {"admin_usuarios", "admin_creditos"} <= admin
        assert _dado(_tool(c, "meus_creditos", {}, _jwt()))["disponivel_usd"] == 20.0
        negado = _dado(_tool(c, "admin_creditos", {"email": "a@x.com", "somar_usd": 500, "motivo": "x"}, _jwt()))
        assert negado["ok"] is False
        ok = _dado(_tool(c, "admin_creditos", {"email": "a@x.com", "somar_usd": 10, "motivo": "rodada"}, _jwt(email=DONO)))
        assert ok["teto_usd"] == 30.0
    linhas = [json.loads(l) for l in capsys.readouterr().out.splitlines() if '"tool"' in l]
    assert any(l["quem"] == DONO and l["tool"] == "admin_creditos" for l in linhas)


# ------------------------------------------------------------ URL com token
from infinito_mcp.modulos import gemini  # noqa: E402
from infinito_mcp.tokens import Tokens  # noqa: E402

TOKEN_ADMIN = "token-admin-de-teste-so-no-ambiente"


def _cliente_token(estado):
    asgi = server.app(None, estado=estado, literatura=ArmazemMemoria(),
                      env={"INF_REPO": str(REPO), "INF_TOKEN_ADMIN": TOKEN_ADMIN, "INF_URL_BASE": "https://inf.exemplo.app"})
    return TestClient(asgi, base_url="https://inf.exemplo.app")


def _tool_url(c, token, nome, args):
    cab = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    return c.post(f"/mcp/{token}/", headers=cab, json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                                      "params": {"name": nome, "arguments": args}})


def test_token_guardado_em_claro_no_ledger_vaza_com_o_bucket():
    est = ArmazemMemoria()
    t = Tokens(est)
    tok = t.emitir("Dudu", "dudu@x.com")
    assert tok.encode() not in est.ler("acesso/tokens.json")
    assert t.decidir(tok).quem == "dudu@x.com"


def test_token_errado_ou_revogado_responde_diferente_de_404():
    est = ArmazemMemoria()
    t = Tokens(est)
    tok = t.emitir("Dudu", "dudu@x.com")
    t.revogar("dudu@x.com")
    with _cliente_token(est) as c:
        for ruim in (tok, "inventado", ""):
            assert _tool_url(c, ruim, "meus_creditos", {}).status_code == 404
        assert c.post("/mcp", json={}).status_code == 404       # sem token no caminho


def test_convite_pela_mcp_interna_vira_url_que_funciona_e_revogar_corta(capsys):
    est = ArmazemMemoria()
    with _cliente_token(est) as c:
        # colaborador não convida
        tok_fraco = Tokens(est).emitir("Fraco", "fraco@x.com")
        assert _dado(_tool_url(c, tok_fraco, "admin_convidar", {"nome": "X", "email": "x@x.com"}))["ok"] is False
        convite = _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "Dudu", "email": "dudu@x.com"}))
        assert convite["ok"] and convite["url"].startswith("https://inf.exemplo.app/mcp/")
        tok = convite["url"].split("/mcp/")[1].strip("/")
        assert _dado(_tool_url(c, tok, "meus_creditos", {}))["disponivel_usd"] == 20.0
        _dado(_tool_url(c, TOKEN_ADMIN, "admin_creditos", {"email": "dudu@x.com", "somar_usd": 10, "motivo": "busca"}))
        assert _dado(_tool_url(c, tok, "meus_creditos", {}))["teto_usd"] == 30.0
        assert _dado(_tool_url(c, TOKEN_ADMIN, "admin_revogar", {"email": "dudu@x.com"}))["tokens_revogados"] == 1
        assert _tool_url(c, tok, "meus_creditos", {}).status_code == 404
        assert "dudu@x.com" in json.dumps(_dado(_tool_url(c, TOKEN_ADMIN, "admin_acessos", {})))
    assert tok not in capsys.readouterr().out          # o token não vai para a auditoria nem para o log


def test_convite_da_pessoa_onze_emite_token_antes_de_recusar_lotado():
    est = ArmazemMemoria()
    with _cliente_token(est) as c:
        for i in range(10):
            assert _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": f"p{i}", "email": f"p{i}@x.com"}))["ok"]
        antes = est.ler("acesso/tokens.json")
        assert _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "p10", "email": "p10@x.com"}))["ok"] is False
        assert est.ler("acesso/tokens.json") == antes


# -------------------------------------------------------------------- gemini
def _gem(chamada, env=None, c=None):
    c = c or creditos()
    ctx = _Ctx(c, env=env or {"INF_REPO": str(REPO), "GEMINI_API_KEY": "k"})
    gemini.registrar(ctx, chamada)
    return ctx, c


def test_gemini_cobra_o_estimado_em_vez_dos_tokens_medidos():
    ctx, c = _gem(lambda m, p, n: {"texto": "oi", "entrada": 1000, "saida": 500})
    r = ctx.tools["gemini"]("a" * 300, confirmar=True)
    p = gemini.PRECOS_PADRAO["gemini-3.8-flash"]
    esperado = round((1000 * p[0] + 500 * p[1]) / 1e6, 6)
    assert r["custo_usd"] == esperado
    assert c.saldo("a@x.com")["gasto_usd"] == esperado and c.saldo("a@x.com")["reservado_usd"] == 0


def test_gemini_seco_nao_chama_a_api_nem_reserva():
    chamadas = []
    ctx, c = _gem(lambda m, p, n: chamadas.append(1))
    r = ctx.tools["gemini"]("oi")
    assert r["seco"] and r["custo_maximo_usd"] > 0 and not chamadas
    assert c.saldo("a@x.com")["reservado_usd"] == 0


def test_gemini_que_falha_ou_sem_chave_continua_cobrando():
    def cai(m, p, n):
        raise TimeoutError

    ctx, c = _gem(cai)
    assert ctx.tools["gemini"]("oi", confirmar=True)["ok"] is False
    ctx2, c2 = _gem(None, env={"INF_REPO": str(REPO)})
    assert "nenhum backend" in ctx2.tools["gemini"]("oi", confirmar=True)["erro"]
    assert c.saldo("a@x.com")["disponivel_usd"] == 20.0 == c2.saldo("a@x.com")["disponivel_usd"]


def test_gemini_com_saldo_curto_chama_assim_mesmo():
    chamadas = []
    ctx, c = _gem(lambda m, p, n: chamadas.append(1) or {"texto": "", "entrada": 1, "saida": 1})
    c.definir(DONO, "a@x.com", teto_usd=0.0, motivo="zerado")
    with pytest.raises(ErroCreditos, match="insuficiente"):
        ctx.tools["gemini"]("oi", max_saida=8192, confirmar=True)
    assert chamadas == []
    assert ctx.tools["gemini"]("oi", modelo="inexistente")["ok"] is False


def test_vaga_de_quem_foi_revogado_continua_ocupada():
    c = creditos(max_usuarios=1)
    c.definir(DONO, "a@x.com", teto_usd=20, motivo="convite")
    c.definir(DONO, "a@x.com", ativo=False, motivo="saiu")
    c.definir(DONO, "b@x.com", teto_usd=20, motivo="convite")      # a vaga voltou
    with pytest.raises(ErroCreditos, match="lotado"):
        c.definir(DONO, "c@x.com", teto_usd=20, motivo="convite")
    assert c.saldo("b@x.com")["teto_usd"] == 20.0


def test_upload_privado_manda_acl_e_o_bucket_uniforme_recusa_com_400():
    from infinito_mcp.armazem import ArmazemGCS
    urls = []
    a = ArmazemGCS("b", token=lambda: "t")
    a._pedir = lambda metodo, url, dados=None, tipo=None: urls.append(url) or (200, b"{}")
    a.por("creditos/usuarios.json", b"{}", "application/json", publico=False)
    assert "predefinedAcl" not in urls[0]
    a.por("x", b"{}", "application/json", publico=True)
    assert "predefinedAcl=publicRead" in urls[1]


def test_admin_convidado_por_e_mail_come_uma_das_dez_vagas():
    est = ArmazemMemoria()
    env = {"INF_REPO": str(REPO), "INF_TOKEN_ADMIN": TOKEN_ADMIN, "INF_URL_BASE": "https://inf.exemplo.app",
           "INF_ADMINS": DONO, "INF_MAX_USUARIOS": "1"}
    asgi = server.app(None, estado=est, literatura=ArmazemMemoria(), env=env)
    with TestClient(asgi, base_url="https://inf.exemplo.app") as c:
        assert _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "p", "email": "p@x.com"}))["ok"]
        r = _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "Dono", "email": DONO}))
        assert r["ok"] and r["nova_vaga"] is False
        tok = r["url"].split("/mcp/")[1].strip("/")
        assert _dado(_tool_url(c, tok, "meus_creditos", {}))["admin"] is True
        nomes = {t["name"] for t in _rpc_url(c, tok, "tools/list")["result"]["tools"]}
        assert "admin_creditos" in nomes
        assert _dado(_tool_url(c, tok, "admin_usuarios", {}))["vagas"] == 0     # o admin não ocupou vaga


def _rpc_url(c, token, metodo):
    cab = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    return c.post(f"/mcp/{token}/", headers=cab, json={"jsonrpc": "2.0", "id": 1, "method": metodo, "params": {}}).json()


def test_vertex_chama_global_com_o_token_da_sa_e_cobra_pensamento_como_saida():
    vistos = {}

    def post(url, corpo, cab):
        vistos.update(url=url, cab=cab, corpo=corpo)
        return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}],
                "usageMetadata": {"promptTokenCount": 6, "thoughtsTokenCount": 17}}

    chamar = gemini.chamar_vertex("proj-x", token=lambda: "TOK", post=post)
    r = chamar("gemini-3.8-flash", "oi", 20)
    assert vistos["url"] == ("https://aiplatform.googleapis.com/v1/projects/proj-x/locations/global/"
                             "publishers/google/models/gemini-3.8-flash:generateContent")
    assert vistos["cab"]["Authorization"] == "Bearer TOK" and "x-goog-api-key" not in vistos["cab"]
    assert (r["texto"], r["entrada"], r["saida"]) == ("ok", 6, 17)       # o pensamento é cobrado como saída


def test_backend_vertex_ligado_pelo_ambiente_substitui_a_chave_sem_credito():
    ctx = _Ctx(creditos(), env={"INF_REPO": str(REPO), "INF_GEMINI_BACKEND": "vertex", "INF_GCP_PROJETO": "p",
                                "GEMINI_API_KEY": "chave-sem-credito"})
    gemini.registrar(ctx)
    assert ctx.tools["gemini"]("oi")["seco"] is True           # registra sem exigir chave nem rede


def test_resposta_cortada_pelo_pensamento_vem_com_fim_max_tokens():
    def post(url, corpo, cab):
        return {"candidates": [{"content": {"parts": [{"text": "Draft"}]}, "finishReason": "MAX_TOKENS"}],
                "usageMetadata": {"promptTokenCount": 19, "thoughtsTokenCount": 190, "candidatesTokenCount": 6}}

    ctx, c = _gem(gemini.chamar_vertex("p", token=lambda: "T", post=post))
    r = ctx.tools["gemini"]("oi", confirmar=True)
    assert r["fim"] == "MAX_TOKENS" and r["tokens_saida"] == 196


def test_admin_ve_quem_usa_ordenado_e_o_proprio_admin_nao_polui_a_lista():
    est = ArmazemMemoria()
    with _cliente_token(est) as c:
        a = _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "Colaborador 01", "email": "c1@x.com"}))
        b = _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "Colaborador 02", "email": "c2@x.com"}))
        ta, tb = (r["url"].split("/mcp/")[1].strip("/") for r in (a, b))
        _tool_url(c, ta, "meus_creditos", {})
        _tool_url(c, tb, "codigos", {})
        _tool_url(c, tb, "codigos", {})
        time.sleep(1.1)                                            # c1 passa a ser o mais recente
        _tool_url(c, ta, "celula", {"id": "K7(9,4)"})
        r = _dado(_tool_url(c, TOKEN_ADMIN, "admin_usuarios", {}))
    assert [p["quem"] for p in r["pessoas"]] == ["c1@x.com", "c2@x.com"]
    c1, c2 = r["pessoas"]
    assert (c1["nome"], c1["chamadas"], c2["chamadas"]) == ("Colaborador 01", 2, 2)
    assert c2["tools_mais_usadas"][0] == "codigos (2)" and c1["ultima_atividade"].endswith("Z")
    assert r["usando"] == 2 and "servico:factory" not in json.dumps(r)


def test_atividade_que_falha_ao_gravar_derruba_a_tool():
    class Quebra(ArmazemMemoria):
        def por(self, nome, dados, tipo, *, publico):
            if nome.startswith("atividade/"):
                raise OSError("bucket fora")
            super().por(nome, dados, tipo, publico=publico)

    est = Quebra()
    with _cliente_token(est) as c:
        tok = _dado(_tool_url(c, TOKEN_ADMIN, "admin_convidar", {"nome": "X", "email": "x@x.com"}))["url"].split("/mcp/")[1].strip("/")
        assert _dado(_tool_url(c, tok, "meus_creditos", {}))["ok"] is True


# --------------------------------------------------------------- executor da VM
from infinito_mcp.executor_vm import ExecutorVM  # noqa: E402


class ComputeFalso:
    """Mini Compute Engine: guarda o estado da instância e responde como a API."""

    def __init__(self, status="TERMINATED", sched_ok=True):
        self.inst = {"status": status, "metadata": {"fingerprint": "f1", "items": [{"key": "ssh-keys", "value": "thiago:ssh-rsa AAA"}]},
                     "lastStartTimestamp": "2026-10-03T10:00:00.000-07:00", "lastStopTimestamp": "2026-10-03T10:30:00.000-07:00"}
        self.chamadas, self.sched_ok, self.guest = [], sched_ok, {}

    def __call__(self, metodo, url, corpo):
        caminho = url.split("/instances/lean-build2")[1]
        self.chamadas.append((metodo, caminho))
        if caminho == "" and metodo == "GET":
            return 200, self.inst
        if caminho == "/setMetadata":
            self.inst["metadata"] = {"fingerprint": "f2", "items": corpo["items"]}
            return 200, {}
        if caminho == "/setScheduling":
            self.ultimo_scheduling = corpo
            return (200, {}) if self.sched_ok else (400, {"error": "x"})
        if caminho == "/start":
            self.inst["status"] = "RUNNING"
            return 200, {}
        if caminho == "/stop":
            self.inst["status"] = "TERMINATED"
            return 200, {}
        if caminho.startswith("/getGuestAttributes"):
            return 200, {"queryValue": {"items": [{"namespace": "infinito", "key": k, "value": v} for k, v in self.guest.items()]}}
        return 404, {}


def _vm(**kw):
    api = ComputeFalso(**kw)
    return ExecutorVM("proj", http=api, dormir=lambda s: None), api


def test_ligar_a_vm_apaga_a_chave_ssh_do_dono_ou_deixa_o_job_para_sempre():
    vm, api = _vm()
    vm.iniciar("lake_build", {"alvo": "CoveringLean"}, 1.0, "a@x.com", "job1")
    chaves = {i["key"]: i["value"] for i in api.inst["metadata"]["items"]}
    assert chaves["ssh-keys"] == "thiago:ssh-rsa AAA"                       # o que já estava continua
    assert json.loads(chaves["infinito-job"])["id"] == "job1" and chaves["enable-guest-attributes"] == "TRUE"
    assert chaves["startup-script"].startswith("#!/bin/bash") and "shutdown -h now" in chaves["startup-script"]
    assert [c for c in api.chamadas if c[0] == "POST"][-1] == ("POST", "/start")
    vm.liberar()
    assert [c for c in api.chamadas if c[1] == "/setScheduling"][-1] and "maxRunDuration" not in api.ultimo_scheduling
    assert "infinito-job" not in {i["key"] for i in api.inst["metadata"]["items"]}
    assert {i["key"] for i in api.inst["metadata"]["items"]} >= {"ssh-keys", "startup-script"}


def test_vm_ocupada_liga_por_cima_e_dobra_a_conta():
    vm, api = _vm(status="RUNNING")
    with pytest.raises(ErroCreditos, match="ocupada"):
        vm.iniciar("lake_build", {}, 1.0, "a@x.com", "j")
    assert not any(c[0] == "POST" for c in api.chamadas)                   # nem mexeu nos metadados


def test_paraquedas_de_duracao_maxima_que_falha_impede_o_job():
    vm, api = _vm(sched_ok=False)
    info = vm.iniciar("lake_build", {}, 1.0, "a@x.com", "j")
    assert info["paraquedas_maxrunduration"] is False and api.inst["status"] == "RUNNING"


def test_status_de_job_alheio_vaza_o_resultado_do_job_anterior():
    vm, api = _vm()
    api.guest = {"id": "outro", "estado": "concluido", "codigo": "0", "saida": "log do outro"}
    s = vm.status("meu")
    assert (s["estado"], s["saida"], s["codigo"]) == (None, "", None)
    api.guest["id"] = "meu"
    s = vm.status("meu")
    assert (s["estado"], s["codigo"], s["saida"]) == ("concluido", 0, "log do outro")
    assert s["inicio_vm"] < s["fim_vm"]


def test_script_da_vm_so_conhece_a_allowlist_e_desliga_a_maquina():
    sh = (AQUI / "infinito_mcp" / "vm" / "job.sh").read_text()
    assert "lake_build" in sh and "verificar_grande" in sh and "shutdown -h now" in sh
    assert 'eval "$CMD"' in sh and "fullmatch" in sh                      # o comando sai de regex, não do pedido
    assert "|| exit 0" in sh                                              # boot manual sem job não faz nada
