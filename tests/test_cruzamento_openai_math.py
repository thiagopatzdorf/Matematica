"""Testes do cruzamento estrutural com o openai/math (tools/literatura/cruzamento_openai_math.py).

O que pode dar errado sem ninguém ver: o parser do CONTENTS.md pendurar manuscrito na família errada
(o ranking inteiro fica deslocado), e a nota "por estrutura" virar só similaridade de texto.
"""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "cruzamento", RAIZ / "tools" / "literatura" / "cruzamento_openai_math.py")
cz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cz)

CONTENTS = """<tbody><tr>
<td>

**133. The computational complexity of Weisfeiler–Leman refinement.** Proves $`n^{\\Omega(k)}`$ bounds. ([Lean](lean/docs/133.md))

</td>
</tr></tbody>
<tbody><tr>
<td>

&emsp;[Parity lifts](preprints/Parity-lifts/paper.pdf)

For <i>k</i> &ge; 4, we construct two graphs.

</td>
</tr></tbody>
<tbody><tr>
<td>

**179. The circulant Hadamard and Barker-sequence conjectures.** Proves circulant Hadamard.

</td>
</tr></tbody>
<tbody><tr>
<td>

&emsp;[The circulant Hadamard conjecture](preprints/circ/paper.pdf)

Orders 1 and 4.

</td>
</tr></tbody>"""


def test_manuscrito_fica_pendurado_na_familia_que_vem_antes_dele():
    fams = cz.ler_contents(CONTENTS)
    assert [f["familia"] for f in fams] == ["133", "179"]
    assert [m["caminho"] for m in fams[0]["manuscritos"]] == ["preprints/Parity-lifts/paper.pdf"]
    assert [m["titulo"] for m in fams[1]["manuscritos"]] == ["The circulant Hadamard conjecture"]


def test_resumo_perde_html_crases_e_link_do_lean():
    fams = cz.ler_contents(CONTENTS)
    assert "Lean" not in fams[0]["resumo"] and "`" not in fams[0]["resumo"]
    assert fams[0]["manuscritos"][0]["resumo"] == "For k ≥ 4, we construct two graphs."


def test_manuscrito_sem_familia_antes_falha_alto():
    with pytest.raises(ValueError):
        cz.ler_contents("<td>\n&emsp;[x](y.pdf) z\n</td>")


def test_disciplina_vem_da_secao_em_que_a_familia_aparece():
    tex = "\\cataloguesection{Number theory}{1}\n\\resultentry{001}{a}\n\\cataloguesection{Combinatorics}{13}\n\\resultentry{179}{b}"
    assert cz.ler_disciplinas(tex) == {"001": "Number theory", "179": "Combinatorics"}


def test_textos_diferentes_com_mesmo_perfil_de_etiquetas_casam_mais_que_texto_parecido_sem_estrutura():
    # 4 unidades em 3 dimensões; 2 etiquetas. A unidade 0 (deles) tem texto ortogonal à frente 2,
    # mas o mesmo perfil de etiqueta; a unidade 1 tem texto próximo da frente 3 e perfil oposto.
    U = cz._normaliza(np.array([[1, 0, 0], [0, 1, 0.1], [0, 0, 1], [0, 1, 0]], dtype=float))
    Z = np.array([[2.0, -1.0], [-1.0, 2.0], [2.0, -1.0], [-1.0, 2.0]])
    notas = cz.pontuar_pares(U, Z, [0, 1], [2, 3])
    assert notas[0, 0] == pytest.approx(0.5)  # cos direto 0, estrutura 1
    assert notas[0, 0] > notas[0, 1]


def test_familia_conta_pelo_manuscrito_mais_forte_e_ranking_e_decrescente():
    notas = np.array([[0.1, 0.9], [0.8, 0.2], [0.3, 0.4]])
    pares = cz.melhores_por_familia(notas, ["133", "133.0", "179.0"], ["F15", "F17"], 10)
    assert pares[0] == {"familia": "133", "frente": "F17", "nota": 0.9, "unidade": "133"}
    assert {(p["familia"], p["frente"]) for p in pares} == {("133", "F15"), ("133", "F17"), ("179", "F15"), ("179", "F17")}
    assert [p["nota"] for p in pares] == sorted((p["nota"] for p in pares), reverse=True)


def test_frente_especifica_nao_some_atras_de_frente_generica():
    # Frente A (genérica) dá nota alta a todo mundo; frente B só à família 162. No ranking global
    # a 162 x B ficaria atrás de qualquer par com A; no ranking por frente ela é a primeira de B.
    notas = np.array([[0.90, 0.80], [0.89, 0.50], [0.88, 0.50], [0.87, 0.51]])
    ids = ["162", "001", "002", "003"]
    global_ = cz.melhores_por_familia(notas, ids, ["A", "B"], 4)
    assert all(p["frente"] == "A" for p in global_)
    pf = cz.por_frente(notas, ids, ["A", "B"], 2)
    assert pf["B"][0]["familia"] == "162" and pf["B"][0]["z"] > 1.5
