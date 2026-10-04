"""Avaliadores (evaluators/): contrato, covering_code, lean_honesty e ponte_ledger.

Cada teste tem nome que descreve a falha que ele pega. Precisa de um compilador C (cc/gcc) só nos
testes de covering_code.
"""
import itertools
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ))
from evaluators import base  # noqa: E402
from evaluators.lean_honesty import declaracoes, limpar_lean  # noqa: E402

CODES = RAIZ / "data" / "codes"
tem_cc = pytest.mark.skipif(not (shutil.which("cc") or shutil.which("gcc")), reason="sem compilador C")
CAMPOS = {"avaliador", "versao", "ok", "veredito", "evidencia", "sha256_arquivo", "sha256_canonico",
          "tempo_s", "comando_reproducao"}


def cli(*args):
    return subprocess.run([sys.executable, "-m", "evaluators", *map(str, args)], cwd=RAIZ,
                          capture_output=True, text=True)


# ---------------------------------------------------------------- contrato
def test_registro_expoe_os_tres_avaliadores_e_recusa_id_desconhecido():
    assert base.ids() == ["covering_code", "lean_honesty", "ponte_ledger"]
    with pytest.raises(KeyError):
        base.obter("nao_existe")
    assert cli("nao_existe", "x").returncode == 2


@tem_cc
def test_resultado_em_json_traz_todos_os_campos_do_contrato_incluindo_os_dois_sha256():
    r = cli("covering_code", CODES / "q5_n9_R5_M50.txt", "--json")
    assert r.returncode == 0, r.stdout + r.stderr
    d = json.loads(r.stdout)
    assert set(d) == CAMPOS
    assert d["ok"] is True and d["sha256_arquivo"] and d["sha256_canonico"] and d["comando_reproducao"]


# ---------------------------------------------------------------- covering_code
def _tira_uma_palavra(tmp_path, origem="q5_n7_R2_M500.txt"):
    q, n, R, M = 5, 7, 2, 500
    palavras = (CODES / origem).read_text().split()[1:]
    arq = tmp_path / f"q{q}_n{n}_R{R}_M{M - 1}.txt"
    arq.write_text("\n".join(palavras) + "\n")
    return arq, palavras, (q, n, R)


@tem_cc
def test_codigo_com_uma_palavra_removida_reprova_e_lista_pontos_realmente_descobertos(tmp_path):
    arq, palavras, (q, n, R) = _tira_uma_palavra(tmp_path)
    r = cli("covering_code", arq, "--json", "--opt", "pontos=8")
    assert r.returncode == 1
    ev = json.loads(r.stdout)["evidencia"]
    assert ev["uncovered"] > 0 and len(ev["pontos_descobertos"]) == 8
    # conferência independente, em Python puro: distância de Hamming a TODA palavra é > R
    cod = [tuple(map(int, w)) for w in palavras]
    for p in ev["pontos_descobertos"]:
        x = tuple(map(int, p))
        assert len(x) == n and all(0 <= d < q for d in x)
        assert min(sum(a != b for a, b in zip(x, c)) for c in cod) > R, p
    assert len(set(ev["pontos_descobertos"])) == 8


@tem_cc
def test_contagem_de_descobertos_do_avaliador_bate_com_forca_bruta(tmp_path):
    arq, palavras, (q, n, R) = _tira_uma_palavra(tmp_path)
    cod = [tuple(map(int, w)) for w in palavras]
    bruto = sum(1 for x in itertools.product(range(q), repeat=n)
                if all(sum(a != b for a, b in zip(x, c)) > R for c in cod))
    ev = json.loads(cli("covering_code", arq, "--json").stdout)["evidencia"]
    assert ev["uncovered"] == bruto > 0


@tem_cc
def test_sem_opcao_u_o_verificador_c_continua_com_a_saida_antiga(tmp_path):
    arq, _, _ = _tira_uma_palavra(tmp_path)
    binario = tmp_path / "v"
    subprocess.run(["cc", "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", binario,
                    RAIZ / "tools/verify/verify.c"], check=True)
    out = subprocess.run([binario, arq], capture_output=True, text=True)
    assert out.returncode == 1 and "uncovered_point" not in out.stdout and len(out.stdout.splitlines()) == 1


@tem_cc
def test_contagem_de_palavras_diferente_do_nome_do_arquivo_e_formato_invalido_nao_cobertura(tmp_path):
    palavras = (CODES / "q5_n7_R2_M500.txt").read_text().split()[1:]
    arq = tmp_path / "q5_n7_R2_M500.txt"  # nome diz 500, o conteúdo tem 499
    arq.write_text("\n".join(palavras) + "\n")
    r = cli("covering_code", arq, "--json")
    d = json.loads(r.stdout)
    assert not d["ok"] and "499" in d["veredito"] and "pontos_descobertos" not in d["evidencia"]


def test_sem_compilador_a_mensagem_e_clara_e_o_codigo_de_saida_e_2(tmp_path, monkeypatch):
    from evaluators import covering_code
    monkeypatch.delenv("EVALUATORS_VERIFY_BIN", raising=False)
    monkeypatch.setattr(covering_code, "_compilador", lambda: None)
    r = covering_code.CoveringCode().executar(CODES / "q5_n9_R5_M50.txt")
    assert not r.ok and r.erro_de_ambiente and "sem compilador C" in r.veredito
    assert r.sha256_arquivo  # o sha do arquivo sai mesmo assim


def test_sha256_do_ledger_e_o_do_arquivo_e_difere_do_canonico_quando_o_txt_nao_esta_ordenado():
    ex = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
    cel = next(c for c in ex if c["id"] == "K5(9,4)")["ours_lean"]
    arq = RAIZ / cel["file"]
    palavras = arq.read_text().split()
    assert cel["sha256"] == base.sha256_arquivo(arq) != base.sha256_canonico(palavras)
    assert palavras != sorted(palavras)


# ---------------------------------------------------------------- lean_honesty
def _lean(tmp_path, texto, nome="X.lean"):
    d = tmp_path / "CoveringLean"
    d.mkdir(exist_ok=True)
    (d / nome).write_text(texto)
    return d


def _honesty(d):
    return base.obter("lean_honesty").executar(d)


def test_sorry_e_native_decide_so_em_comentario_nao_dao_falso_alarme(tmp_path):
    d = _lean(tmp_path, '/-- Sem `sorry`, sem `native_decide`, sem axioma. -/\n-- nenhum sorry aqui\n'
                        '/-! nota: nada de native_decide -/\ntheorem t : 1 + 1 = 2 := by decide\n')
    r = _honesty(d)
    assert r.ok, r.veredito
    assert r.evidencia["mencoes_so_em_comentario_ou_string"]["sorry"]["ocorrencias"] == 2


def test_uso_real_de_sorry_native_decide_e_axiom_e_reprovado_com_linha(tmp_path):
    d = _lean(tmp_path, "theorem a : 1 = 1 := sorry\ntheorem b : 2 = 2 := by native_decide\n"
                        "axiom ax : False\nprivate axiom ay : False\n")
    r = _honesty(d)
    assert not r.ok
    tipos = {(a["tipo"], a["linha"]) for a in r.evidencia["achados"]}
    assert tipos == {("sorry", 1), ("native_decide", 2), ("axiom", 3), ("axiom", 4)}


def test_comentario_aninhado_esconde_sorry_mas_o_codigo_depois_do_fecho_nao(tmp_path):
    d = _lean(tmp_path, "/- fora /- dentro sorry -/ ainda comentario native_decide -/\n"
                        "theorem a : 1 = 1 := rfl\ntheorem b : 2 = 2 := sorry\n")
    r = _honesty(d)
    assert [(a["tipo"], a["linha"]) for a in r.evidencia["achados"]] == [("sorry", 3)]


def test_sorry_dentro_de_string_nao_conta_mas_aspas_escapadas_nao_fecham_a_string(tmp_path):
    d = _lean(tmp_path, 'def s := "diz sorry e native_decide"\ndef t := "aspas \\" sorry ainda string"\n'
                        "def c := \'\"\'\ntheorem a : 1 = 1 := by decide\n")
    assert _honesty(d).ok


def test_comentario_de_linha_dentro_de_string_nao_abre_comentario_e_o_sorry_depois_conta(tmp_path):
    d = _lean(tmp_path, 'def s := "-- nao e comentario"; theorem a : 1 = 1 := sorry\n')
    assert not _honesty(d).ok


def test_declaracao_axiom_comentada_nao_conta_e_a_palavra_axioms_do_print_tambem_nao(tmp_path):
    d = _lean(tmp_path, "-- axiom foo : False\ntheorem a : 1 = 1 := rfl\n#print axioms a\n")
    assert _honesty(d).ok


def test_limpar_lean_preserva_comprimento_e_quebras_de_linha():
    t = "a /- x\n y -/ b -- c\n\"s\\n\" d\n"
    assert len(limpar_lean(t)) == len(t)
    assert limpar_lean(t).count("\n") == t.count("\n")


def test_declaracoes_usam_o_namespace_e_ignoram_declaracao_comentada():
    t = limpar_lean("namespace Syn\ntheorem a : True := trivial\nend Syn\n-- theorem b : True\ntheorem SC.c : True := trivial\n")
    assert declaracoes(t) == {"Syn.a", "SC.c"}


def test_repo_real_nao_usa_sorry_native_decide_nem_axiom():
    r = _honesty(RAIZ / "CoveringLean")
    assert r.ok, r.veredito
    assert r.evidencia["arquivos_varridos"] > 400


# ---------------------------------------------------------------- ponte_ledger
@pytest.fixture
def ledger_tmp(tmp_path):
    """Cópia do ledger e de data/codes em tmp; o Lean é o do repo (link), só leitura."""
    (tmp_path / "data").mkdir()
    shutil.copytree(CODES, tmp_path / "data" / "codes")
    (tmp_path / "CoveringLean").symlink_to(RAIZ / "CoveringLean", target_is_directory=True)
    (tmp_path / "ledger").mkdir()
    shutil.copy(RAIZ / "ledger" / "cells.json", tmp_path / "ledger" / "cells.json")
    return tmp_path


def _ponte(tmp, ledger=None):
    return base.obter("ponte_ledger").executar(ledger or tmp / "ledger" / "cells.json", raiz=tmp)


def _muda(tmp, cid, campo, valor):
    p = tmp / "ledger" / "cells.json"
    d = json.loads(p.read_text())
    next(c for c in d["cells"] if c["id"] == cid)["ours_lean"][campo] = valor
    p.write_text(json.dumps(d))


def test_ponte_do_repo_real_fecha_sem_divergencia():
    r = base.obter("ponte_ledger").executar(None)
    assert r.ok, r.veredito
    assert r.evidencia["celulas_conferidas"] >= 12


def test_ponte_reprova_quando_o_M_do_ledger_e_alterado(ledger_tmp):
    _muda(ledger_tmp, "K5(7,2)", "M", 499)
    r = _ponte(ledger_tmp)
    assert not r.ok
    a = next(x for x in r.evidencia["achados"] if x["checagem"] == "M_ledger_nome_palavras")
    assert (a["celula"], a["ledger"], a["nome"], a["palavras"]) == ("K5(7,2)", 499, 500, 500)


def test_ponte_reprova_quando_o_arquivo_perde_uma_palavra_sem_o_nome_acompanhar(ledger_tmp):
    arq = ledger_tmp / "data" / "codes" / "q5_n9_R5_M50.txt"
    arq.write_text("\n".join(arq.read_text().split()[1:]) + "\n")
    r = _ponte(ledger_tmp)
    achados = {a["checagem"] for a in r.evidencia["achados"]}
    assert not r.ok and {"M_ledger_nome_palavras", "sha256_arquivo"} <= achados


def test_ponte_reprova_declaracao_lean_inexistente_ou_com_namespace_errado(ledger_tmp):
    _muda(ledger_tmp, "K5(9,4)", "declaration", "CoveringKernel.K5_9_4_le_250_inventado")
    _muda(ledger_tmp, "K7(9,4)", "declaration", "K7_9_4_le_1134_syn")  # sem o `Syn.`
    r = _ponte(ledger_tmp)
    cels = {a["celula"] for a in r.evidencia["achados"] if a["checagem"] == "declaracao_existe"}
    assert not r.ok and cels == {"K5(9,4)", "K7(9,4)"}


def test_ponte_reprova_quando_o_nome_da_declaracao_fala_de_outro_M(ledger_tmp):
    _muda(ledger_tmp, "K7(9,4)", "declaration", "Syn.K7_9_4_le_1137_syn")  # existe no repo, mas é outro M
    r = _ponte(ledger_tmp)
    assert any(a["checagem"] == "declaracao_vs_M" for a in r.evidencia["achados"])


def test_ponte_reprova_arquivo_que_pertence_a_outra_celula(ledger_tmp):
    _muda(ledger_tmp, "K5(7,2)", "file", "data/codes/q5_n9_R5_M50.txt")
    r = _ponte(ledger_tmp)
    assert any(a["checagem"] == "arquivo_vs_celula" for a in r.evidencia["achados"])
