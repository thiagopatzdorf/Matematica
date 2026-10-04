"""Registro de problemas: máquina de estados, validador e cartões semeados."""
import copy
import hashlib
import json
import re
import subprocess
import sys

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "problems"))
import lifecycle  # noqa: E402
import seed_from_ledger as seed  # noqa: E402
import validate  # noqa: E402

CARTOES = RAIZ / "problems" / "cartoes"
HASH = "a" * 64


def novo():
    c = {"formato": "cartao-problema/v1", "id": "exemplo-de-problema", "titulo": "Exemplo", "dominio": "teste",
         "tipo": "cota_superior", "enunciado": "Achar um objeto com a propriedade P e tamanho menor.",
         "enunciado_formal": None, "estado": None,
         "melhor_conhecido": {"valor": 10, "fonte": "x", "ref": "y"},
         "nosso": {"valor": None, "estado": "nenhum", "prova": None},
         "avaliador": {"id": "av", "como_rodar": "echo ok", "custo_estimado_usd": 0},
         "celula_ledger": None, "historico": []}
    return lifecycle.transicionar(c, "proposto", "ana", "qualquer", "2026-10-04")


def ate(estado):
    """Leva um cartão novo ao estado pedido pelo caminho legal."""
    c = novo()
    c = lifecycle.transicionar(c, "aceito", "mia", "mantenedor", "2026-10-04")
    c = lifecycle.transicionar(c, "aberto", "mia", "mantenedor", "2026-10-04")
    if estado == "aberto":
        return c
    c = lifecycle.transicionar(c, "candidato", "ana", "qualquer", "2026-10-05", {"artefato": "c.txt", "sha256": HASH})
    c["nosso"] = {"valor": 9, "estado": "computacional", "prova": "c.txt"}
    if estado == "candidato":
        return c
    c = lifecycle.transicionar(c, "verificado", "ci", "avaliador", "2026-10-05",
                               {"avaliador": "av", "veredito": "ok", "saida": '{"ok": true}'})
    if estado == "verificado":
        return c
    c = lifecycle.transicionar(c, "certificado", "ci", "avaliador", "2026-10-06",
                               {"kernel": "lean", "declaracao": "Foo.bar"})
    c["nosso"]["estado"] = "lean"
    return c


def test_certificado_sem_passar_por_verificado_e_recusado():
    with pytest.raises(lifecycle.TransicaoIlegal, match="candidato -> certificado"):
        lifecycle.transicionar(ate("candidato"), "certificado", "ci", "avaliador", "2026-10-06",
                               {"kernel": "lean", "declaracao": "Foo.bar"})


def test_certificado_sem_evidencia_do_kernel_lean_e_recusado():
    with pytest.raises(lifecycle.TransicaoIlegal, match="kernel"):
        lifecycle.transicionar(ate("verificado"), "certificado", "ci", "avaliador", "2026-10-06", {})


def test_verificado_sem_saida_do_avaliador_e_recusado():
    with pytest.raises(lifecycle.TransicaoIlegal, match="saida"):
        lifecycle.transicionar(ate("candidato"), "verificado", "ci", "avaliador", "2026-10-06",
                               {"avaliador": "av", "veredito": "ok"})


def test_verificado_com_avaliador_de_outro_cartao_e_recusado():
    with pytest.raises(lifecycle.TransicaoIlegal, match="avaliador"):
        lifecycle.transicionar(ate("candidato"), "verificado", "ci", "avaliador", "2026-10-06",
                               {"avaliador": "outro", "veredito": "ok", "saida": "x"})


def test_verificado_com_veredito_que_nao_e_ok_e_recusado():
    with pytest.raises(lifecycle.TransicaoIlegal, match="veredito"):
        lifecycle.transicionar(ate("candidato"), "verificado", "ci", "avaliador", "2026-10-06",
                               {"avaliador": "av", "veredito": "falhou", "saida": "x"})


def test_so_o_dono_publica_e_so_o_mantenedor_aceita():
    with pytest.raises(lifecycle.TransicaoIlegal, match="publicado"):
        lifecycle.transicionar(ate("certificado"), "publicado", "mia", "mantenedor", "2026-10-07")
    assert lifecycle.transicionar(ate("certificado"), "publicado", "thiago", "dono", "2026-10-07")["estado"] == "publicado"
    with pytest.raises(lifecycle.TransicaoIlegal, match="aceito"):
        lifecycle.transicionar(novo(), "aceito", "ana", "qualquer", "2026-10-04")


def test_importacao_nunca_publica():
    with pytest.raises(lifecycle.TransicaoIlegal, match="importação"):
        lifecycle.checar({}, "certificado", "publicado", "x", "dono", "2026-10-04", {}, importacao=True)


def test_estado_terminal_arquivado_nao_tem_saida():
    c = lifecycle.transicionar(novo(), "arquivado", "mia", "mantenedor", "2026-10-05", {"motivo": "duplicado"})
    for destino in lifecycle.ESTADOS:
        with pytest.raises(lifecycle.TransicaoIlegal):
            lifecycle.transicionar(c, destino, "mia", "mantenedor", "2026-10-06", {"motivo": "x", "ref": "y"})


def test_reivindicacao_exige_prazo_de_no_maximo_30_dias_e_expira():
    c = ate("aberto")
    for exp in (None, "2026-10-04", "2026-12-31"):
        with pytest.raises(lifecycle.TransicaoIlegal, match="expira_em"):
            lifecycle.transicionar(c, "reivindicado", "ana", "qualquer", "2026-10-04", {"expira_em": exp} if exp else {})
    r = lifecycle.transicionar(c, "reivindicado", "ana", "qualquer", "2026-10-04", {"expira_em": "2026-10-20"})
    assert lifecycle.expirar(r, "2026-10-20") is r  # no último dia ainda vale
    v = lifecycle.expirar(r, "2026-10-21")
    assert v["estado"] == "aberto" and v["historico"][-1]["quem"] == "sistema"
    assert lifecycle.verificar_historico(v) == []


def test_candidato_de_reivindicacao_so_vem_de_quem_reivindicou():
    r = lifecycle.transicionar(ate("aberto"), "reivindicado", "ana", "qualquer", "2026-10-04", {"expira_em": "2026-10-20"})
    ev = {"artefato": "c.txt", "sha256": HASH}
    with pytest.raises(lifecycle.TransicaoIlegal, match="reivindicado por ana"):
        lifecycle.transicionar(r, "candidato", "beto", "qualquer", "2026-10-05", ev)
    assert lifecycle.transicionar(r, "candidato", "ana", "qualquer", "2026-10-05", ev)["estado"] == "candidato"


def test_caminho_legal_completo_gera_cartao_valido():
    c = lifecycle.transicionar(ate("certificado"), "publicado", "thiago", "dono", "2026-10-07")
    assert validate.validar_cartao(c) == []


def test_historico_adulterado_com_salto_de_estado_e_reprovado():
    c = ate("verificado")
    c["historico"].pop(3)  # some o `candidato`: verificado passa a vir de aberto
    assert any("historico" in e for e in validate.validar_cartao(c))


def test_estado_que_nao_bate_com_o_historico_e_reprovado():
    c = ate("verificado")
    c["estado"] = "certificado"
    assert any("difere da última entrada" in e for e in validate.validar_cartao(c))


def test_certificado_sem_prova_lean_em_nosso_e_reprovado():
    c = ate("certificado")
    c["nosso"]["estado"] = "computacional"
    assert any("kernel do Lean" in e for e in validate.validar_cartao(c))


@pytest.mark.parametrize("mutacao,trecho", [
    (lambda c: c.pop("enunciado"), "enunciado"),
    (lambda c: c.update(tipo="outro"), "tipo"),
    (lambda c: c.update(id="Id Ruim"), "id"),
    (lambda c: c.update(extra=1), "desconhecido"),
    (lambda c: c["avaliador"].pop("como_rodar"), "como_rodar"),
    (lambda c: c.update(celula_ledger="K7-9-4"), "celula_ledger"),
])
def test_cartao_com_campo_invalido_e_reprovado(mutacao, trecho):
    c = copy.deepcopy(ate("aberto"))
    mutacao(c)
    assert any(trecho in e for e in validate.validar_cartao(c))


def test_validador_sai_com_codigo_diferente_de_zero_se_algum_cartao_e_invalido(tmp_path):
    ruim = ate("aberto")
    ruim["tipo"] = "palpite"
    f = tmp_path / "exemplo-de-problema.json"
    f.write_text(json.dumps(ruim))
    r = subprocess.run([sys.executable, str(RAIZ / "tools/problems/validate.py"), "--json", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and json.loads(r.stdout)["invalidos"] == 1
    f.write_text(json.dumps(ate("aberto")))
    assert subprocess.run([sys.executable, str(RAIZ / "tools/problems/validate.py"), str(f)],
                          capture_output=True).returncode == 0


def test_nome_do_arquivo_diferente_do_id_e_reprovado(tmp_path):
    f = tmp_path / "outro-nome.json"
    f.write_text(json.dumps(ate("aberto")))
    assert any("deve se chamar" in e for e in validate.validar_arquivo(f))


def test_esquema_json_e_lifecycle_listam_os_mesmos_estados_e_tipos():
    s = json.loads((RAIZ / "problems/schema/cartao.schema.json").read_text(encoding="utf-8"))
    p = s["properties"]
    assert tuple(p["estado"]["enum"]) == lifecycle.ESTADOS
    assert tuple(p["historico"]["items"]["properties"]["para"]["enum"]) == lifecycle.ESTADOS
    assert tuple(p["tipo"]["enum"]) == validate.TIPOS
    assert tuple(p["historico"]["items"]["properties"]["papel"]["enum"]) == lifecycle.PAPEIS
    assert set(s["required"]) == validate.OBRIGATORIOS


# --- cartões semeados: o valor do cartão tem de ser o do ledger / do doc -------------------

def _ledger():
    return {c["id"]: c for c in json.loads((RAIZ / "ledger/cells.json").read_text(encoding="utf-8"))["cells"]}


def _cartoes():
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(CARTOES.glob("*.json"))}


def test_todos_os_cartoes_semeados_sao_validos():
    assert all(not e for e in validate.validar_pasta(CARTOES).values())
    assert len(list(CARTOES.glob("*.json"))) >= 5


@pytest.mark.parametrize("cid", seed.CELULAS)
def test_valor_do_cartao_diverge_do_ledger(cid):
    cel, c = _ledger()[cid], _cartoes()[seed.slug_celula(_ledger()[cid])]
    assert c["celula_ledger"] == cid
    assert c["melhor_conhecido"]["valor"] == cel["published"]["ub"]["value"]
    assert c["melhor_conhecido"]["fonte"] == cel["published"]["ub"]["source"]
    assert c["nosso"]["valor"] == cel["ours_lean"]["M"] == cel["best"]["ub"]
    assert c["nosso"]["prova"] == cel["ours_lean"]["declaration"] == c["enunciado_formal"]
    cand = next(h for h in c["historico"] if h["para"] == "candidato")["evidencia"]
    assert cand["sha256"] == cel["ours_lean"]["sha256"]
    # o sha do ledger é o do arquivo de verdade, não só o que o ledger afirma
    assert hashlib.sha256((RAIZ / cand["artefato"]).read_bytes()).hexdigest() == cand["sha256"]


@pytest.mark.parametrize("cid", seed.CELULAS)
def test_saida_do_verificador_guardada_e_do_codigo_do_cartao(cid):
    cel = _ledger()[cid]
    ev = json.loads((RAIZ / "problems/evidencias" / f"{seed.slug_celula(cel)}.verificador.json").read_text())
    assert ev == {"ok": True, "q": cel["q"], "n": cel["n"], "R": cel["R"], "M": cel["ours_lean"]["M"],
                  "distintas": cel["ours_lean"]["M"], "descobertas": 0}


@pytest.mark.parametrize("cid", seed.CELULAS)
def test_declaracao_lean_do_cartao_existe_no_codigo_fonte(cid):
    decl = _cartoes()[seed.slug_celula(_ledger()[cid])]["nosso"]["prova"]
    ns, nome = decl.split(".", 1)
    fontes = "\n".join(p.read_text(encoding="utf-8") for p in (RAIZ / "CoveringLean").glob("*.lean"))
    assert re.search(rf"theorem {re.escape(nome)}\b", fontes), f"{decl} não existe em CoveringLean/"


def test_k742_do_cartao_bate_com_o_doc_e_com_os_certificados():
    c = _cartoes()["cobertura-k7-4-2-exato"]
    doc = (RAIZ / seed.DOC_K742).read_text(encoding="utf-8")
    assert int(re.search(r"Resultado: K_7\(4,2\) = (\d+)", doc)[1]) == c["nosso"]["valor"] == 19
    lb, ub = re.search(r"Antes: (\d+) ≤ K ≤ (\d+)", doc).groups()
    assert c["melhor_conhecido"]["intervalo"] == {"lb": int(lb), "ub": int(ub)}
    cel = _ledger()["K7(4,2)"]
    assert (c["melhor_conhecido"]["intervalo"]["lb"], c["melhor_conhecido"]["intervalo"]["ub"]) == (
        cel["published"]["lb"]["value"], cel["published"]["ub"]["value"])
    for rel in seed.CERTS_K742:
        linhas = [json.loads(x) for x in (RAIZ / rel).read_text().splitlines()]
        assert linhas and all(x["resultado"] == "UNSAT" and x["lrat_check"] == "VERIFIED" for x in linhas)
    # LRAT conferido (verificado) e depois o teorema incondicional no kernel (certificado, v0.8)
    assert c["estado"] == "certificado" and c["nosso"] == {"valor": 19, "estado": "lean", "prova": "K742.K_7_4_2_eq_19"}
    assert [h["para"] for h in c["historico"]][-2:] == ["verificado", "certificado"]
    assert c["historico"][-1]["evidencia"]["tag"] == cel["certification"]["lb"]["provenance"]["lean"]["tag"]


def test_semear_duas_vezes_gera_bytes_identicos_e_iguais_aos_cartoes_do_repositorio(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    for d in (a, b):
        subprocess.run([sys.executable, str(RAIZ / "tools/problems/seed_from_ledger.py"), "--saida", str(d)],
                       check=True, capture_output=True)
    nomes = sorted(p.name for p in a.glob("*.json"))
    assert nomes == sorted(p.name for p in b.glob("*.json")) == sorted(p.name for p in CARTOES.glob("*.json"))
    for n in nomes:
        assert (a / n).read_bytes() == (b / n).read_bytes() == (CARTOES / n).read_bytes(), n
