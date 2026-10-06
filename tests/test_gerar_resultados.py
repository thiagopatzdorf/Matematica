"""O bloco RESULTADOS do README e os badges são derivados do ledger; aqui se prova que não divergem dele.

Gerador: tools/site/gerar_resultados.py. Se um destes testes falhar depois de mudar o ledger, rode
`python3 tools/site/gerar_resultados.py --escrever README.md` e
`python3 tools/site/gerar_resultados.py --badges docs/badges`.
"""
import importlib.util
import json
import random
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("gerar_resultados", RAIZ / "tools" / "site" / "gerar_resultados.py")
gr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gr)

LEDGER = gr.ler_ledger()
CELLS = LEDGER["cells"]
BLOCO = gr.bloco(LEDGER)
README = RAIZ / "README.md"


def _linhas_da_tabela(bloco):
    return [li for li in bloco.splitlines() if li.startswith("| `K_")]


def _id(c):
    return f"`K_{c['q']}({c['n']},{c['R']})`"


# ---------------------------------------------------------------- README e badges commitados


def test_bloco_do_readme_diverge_do_ledger():
    texto = README.read_text(encoding="utf-8")
    if gr.INICIO not in texto or gr.FIM not in texto:
        pytest.skip("README.md ainda não tem as marcas RESULTADOS (o README novo vem em outro PR); "
                    "o teste passa a valer sozinho quando elas existirem")
    assert gr.substituir(texto, BLOCO) == texto, (
        "README.md desatualizado: rode `python3 tools/site/gerar_resultados.py --escrever README.md`")


def test_badges_commitados_divergem_do_ledger():
    for nome, conteudo in gr.badges(LEDGER).items():
        p = RAIZ / "docs" / "badges" / nome
        assert p.is_file(), f"falta {p.relative_to(RAIZ)}: rode `gerar_resultados.py --badges docs/badges`"
        assert p.read_text(encoding="utf-8") == conteudo, f"{nome} diverge do ledger"


def test_badge_nao_segue_o_esquema_do_shields_io():
    for conteudo in gr.badges(LEDGER).values():
        d = json.loads(conteudo)
        assert d["schemaVersion"] == 1 and d["label"] and d["message"] and d["color"]


# ---------------------------------------------------------------- números


def test_contagem_do_kernel_diverge_de_F_mais_I_do_cobertura():
    """O número de cotas superiores no kernel tem de ser F + I da linha `ub` do COBERTURA.md commitado."""
    cob = (RAIZ / "ledger" / "COBERTURA.md").read_text(encoding="utf-8")
    cab = next(li for li in cob.splitlines() if li.startswith("| lado |"))
    ub = next(li for li in cob.splitlines() if li.startswith("| ub |"))
    col = [x.strip() for x in cab.strip("|").split("|")]
    val = [x.strip() for x in ub.strip("|").split("|")]
    f_mais_i = int(val[col.index("FORMALIZED")]) + int(val[col.index("INDEPENDENTLY_REPRODUCED")])
    n = gr.numeros(LEDGER)
    assert n["kernel"] == f_mais_i
    assert f"**{f_mais_i}** de {n['celulas']}" in BLOCO


def test_exatas_e_abertas_nao_somam_o_total_de_celulas():
    n = gr.numeros(LEDGER)
    assert n["celulas"] == len(CELLS) == LEDGER["meta"]["n_cells"]
    assert n["exatas"] == sum(c["certification"]["exact"] for c in CELLS)
    assert n["exatas"] + n["abertas"] == n["celulas"]


def test_inferiores_por_estado_nao_somam_o_total():
    n = gr.numeros(LEDGER)
    assert sum(n["inferiores_por_estado"].values()) == n["celulas"]
    assert sum(n["superiores_por_estado"].values()) == n["celulas"]


def test_contagem_de_codigos_ignora_arquivo_novo_em_data_codes(tmp_path):
    (tmp_path / "data" / "codes").mkdir(parents=True)
    for p in sorted((RAIZ / "data" / "codes").glob("*.txt"))[:3]:
        (tmp_path / "data" / "codes" / p.name).write_bytes(p.read_bytes())
    (tmp_path / "data" / "codes" / "q2_n3_R1_M2.txt").write_text("000\n111\n")
    r = gr.conferir_codigos(CELLS, tmp_path)
    assert r["arquivos"] == 4
    assert r["testemunhas_do_ledger"] <= 3  # o arquivo novo não tem sha256 no ledger


# ---------------------------------------------------------------- destaques


def test_tabela_perde_uma_exata_certificada():
    linhas = "\n".join(_linhas_da_tabela(BLOCO))
    certificadas = [c for c in CELLS if c["certification"]["lb"]["state"] == "CERTIFICATE_VERIFIED"]
    assert certificadas, "o ledger devia ter cotas inferiores CERTIFICATE_VERIFIED"
    for c in certificadas:
        assert f"| {_id(c)} |" in linhas, f"{c['id']} sumiu dos destaques"


def test_tabela_perde_celula_com_teorema_lean_proprio():
    linhas = "\n".join(_linhas_da_tabela(BLOCO))
    for c in CELLS:
        if c["ours_lean"]:
            assert f"| {_id(c)} |" in linhas, f"{c['id']} sumiu dos destaques"


def test_tabela_inclui_celula_sem_resultado_proprio():
    proprias = {_id(c) for c in CELLS
                if c["ours_lean"] or c["certification"]["lb"]["state"] == "CERTIFICATE_VERIFIED"}
    assert len(_linhas_da_tabela(BLOCO)) == len(proprias)


def test_exata_nova_aparece_depois_de_cota_superior_melhorada():
    ds = gr.destaques(CELLS)
    flags = [d["exata_nova"] for d in ds]
    assert flags == sorted(flags, reverse=True), "exatas novas têm de vir primeiro"
    ganhos = [d["ganho"] for d in ds if not d["exata_nova"]]
    assert ganhos == sorted(ganhos, reverse=True), "depois, maior ganho relativo primeiro"


def test_estado_na_tabela_diverge_do_ledger():
    por_nome = {_id(c): c for c in CELLS}
    for li in _linhas_da_tabela(BLOCO):
        cols = [x.strip() for x in li.strip("|").split("|")]
        c = por_nome[cols[0]]
        assert cols[3] == c["certification"]["lb"]["state"]
        assert cols[4] == c["certification"]["ub"]["state"]
        assert str(c["certification"]["ub"]["value"]) in cols[2]


def test_link_do_bloco_aponta_para_arquivo_que_nao_existe():
    for alvo in re.findall(r"\]\(([^)]+)\)", BLOCO):
        if alvo.startswith("http"):
            continue
        assert (RAIZ / alvo).is_file(), alvo


# ---------------------------------------------------------------- honestidade


def test_bloco_perde_a_frase_obrigatoria_do_ledger():
    assert gr.FRASE_LEDGER in BLOCO


def test_bloco_sugere_que_a_tabela_inteira_e_formal():
    baixo = BLOCO.lower()
    for proibida in ("todas as cotas são teorema", "tabela inteira verificada", "todas verificadas formalmente"):
        assert proibida not in baixo
    assert "**não** estão, em geral, no Lean" in BLOCO


def test_lacuna_de_cota_superior_so_anunciada_some_do_bloco():
    for c in CELLS:
        cert = c["certification"]
        if (c["ours_lean"] or cert["lb"]["state"] == "CERTIFICATE_VERIFIED") and cert["ub"]["state"] == "CLAIMED":
            lacuna = next(li for li in BLOCO.splitlines() if li.startswith("Lacunas declaradas"))
            assert _id(c) in lacuna.split("cota superior de", 1)[1]


# ---------------------------------------------------------------- determinismo e modos


def test_gerador_depende_da_ordem_das_celulas_no_ledger():
    embaralhado = dict(LEDGER, cells=random.Random(7).sample(CELLS, len(CELLS)))
    assert gr.bloco(embaralhado) == BLOCO
    assert gr.badges(embaralhado) == gr.badges(LEDGER)


def test_escrever_sem_marcas_nao_falha_com_mensagem_clara(tmp_path, capsys):
    alvo = tmp_path / "README.md"
    alvo.write_text("# sem marcas\n", encoding="utf-8")
    assert gr.main(["--escrever", str(alvo)]) == 2
    assert "RESULTADOS:INICIO" in capsys.readouterr().err
    assert alvo.read_text(encoding="utf-8") == "# sem marcas\n"


def test_escrever_mexe_fora_das_marcas(tmp_path):
    alvo = tmp_path / "README.md"
    alvo.write_text(f"antes\n{gr.INICIO}\nvelho\n{gr.FIM}\ndepois\n", encoding="utf-8")
    assert gr.main(["--escrever", str(alvo)]) == 0
    t = alvo.read_text(encoding="utf-8")
    assert t.startswith(f"antes\n{gr.INICIO}\n") and t.endswith(f"{gr.FIM}\ndepois\n")
    assert "velho" not in t and BLOCO in t
    assert gr.main(["--checar", str(alvo)]) == 0
    assert gr.main(["--escrever", str(alvo)]) == 0 and alvo.read_text(encoding="utf-8") == t  # idempotente


def test_checar_aceita_readme_desatualizado(tmp_path):
    alvo = tmp_path / "README.md"
    alvo.write_text(f"{gr.INICIO}\n| células | 1144 |\n{gr.FIM}\n", encoding="utf-8")
    assert gr.main(["--checar", str(alvo)]) == 1


def test_marcas_duplicadas_passam_sem_erro():
    with pytest.raises(gr.SemMarcas):
        gr.substituir(f"{gr.INICIO}\n{gr.FIM}\n{gr.INICIO}\n{gr.FIM}\n", BLOCO)
    with pytest.raises(gr.SemMarcas):
        gr.substituir(f"{gr.FIM}\n{gr.INICIO}\n", BLOCO)
