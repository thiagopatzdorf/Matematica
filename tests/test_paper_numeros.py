"""As contagens do ledger que o paper cita saem do ledger, por script; aqui se prova que não divergem.

Gerador: tools/paper/numeros.py -> paper/numeros.tex (macros do LaTeX) e a frase de contagem do
.zenodo.json. Se um destes testes falhar depois de mudar o ledger, rode `python3 tools/paper/numeros.py`.
Antes disto o paper dizia "547 of the 1145" com 642 no ledger (PRs #95 e #98 subiram o ledger e o
texto ficou para trás); uma contagem digitada à mão volta a divergir.
"""
import copy
import importlib.util
import json
import re

from conftest import RAIZ

_spec = importlib.util.spec_from_file_location("paper_numeros", RAIZ / "tools" / "paper" / "numeros.py")
pn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pn)

LEDGER = pn.ler_ledger()
TEX = (RAIZ / "paper" / "main.tex").read_text(encoding="utf-8")
NUMEROS_TEX = (RAIZ / "paper" / "numeros.tex").read_text(encoding="utf-8")


def test_numeros_tex_commitado_diverge_do_ledger():
    assert NUMEROS_TEX == pn.gerar(LEDGER), "paper/numeros.tex desatualizado: rode `python3 tools/paper/numeros.py`"


def test_frase_de_contagem_do_zenodo_diverge_do_ledger():
    z = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
    assert pn.frase_zenodo(LEDGER) in z["description"]


def test_paper_nao_inclui_o_arquivo_de_numeros():
    assert re.search(r"^\\input\{numeros\}", TEX, re.M)


def test_paper_usa_macro_que_o_gerador_nao_define():
    definidas = set(pn.macros(NUMEROS_TEX))
    usadas = set(re.findall(r"\\((?:Num|Exatas|LBVerificada)[A-Za-z]*)", TEX))
    assert usadas and usadas <= definidas, usadas - definidas


def test_paper_digita_a_mao_uma_contagem_do_ledger():
    """Nenhuma contagem do ledger com 3 ou mais algarismos aparece literal no texto (comentários fora).

    Contagens pequenas (2, 3, 5) coincidem com qualquer número da matemática e não dá para proibir; as
    grandes só aparecem por cópia do ledger. Valores históricos (o 547 da v0.9.1) não são do ledger atual.
    """
    sem_comentarios = re.sub(r"(?<!\\)%.*", "", TEX)
    grandes = {v for v in pn.numeros(LEDGER).values() if v.isdigit() and len(v) >= 3}
    achados = {v for v in grandes if _digitado(v, sem_comentarios)}
    assert not achados, f"contagem do ledger digitada no main.tex: {sorted(achados)} (use a macro de numeros.tex)"


def _digitado(v: str, texto: str) -> bool:
    """`v` aparece como número inteiro no texto. O espaço fino do LaTeX (`117\\,649`) separa milhares:
    o pedaço de um número maior não é a contagem (falso positivo medido com 117 no `7^6 = 117\\,649`), nem o
    de um hexadecimal (700 no sha256 `2a700e2f`)."""
    return re.search(rf"(?<![\w.,])(?<!\\,){v}(?![\w.,])(?!\\,\d)", texto) is not None


def test_pedaco_de_numero_ou_de_hexadecimal_nao_conta_como_contagem_digitada():
    assert not _digitado("117", r"sobre as $7^6=117\,649$ palavras")
    assert not _digitado("649", r"sobre as $7^6=117\,649$ palavras")
    assert not _digitado("700", r"\texttt{2a700e2f}")
    assert _digitado("117", r"são $117$ cotas")


def test_gerador_ignora_mudanca_de_estado_no_ledger():
    """Uma cota a mais no kernel muda o arquivo gerado: o gerador lê o ledger, não guarda número."""
    outro = copy.deepcopy(LEDGER)
    alvo = next(c for c in outro["cells"] if c["certification"]["ub"]["state"] == "CLAIMED")
    alvo["certification"]["ub"]["state"] = "FORMALIZED"
    antes, depois = pn.numeros(LEDGER), pn.numeros(outro)
    assert int(depois["NumUBKernel"]) == int(antes["NumUBKernel"]) + 1
    assert int(depois["NumUBForaDoKernel"]) == int(antes["NumUBForaDoKernel"]) - 1
    assert pn.gerar(outro) != pn.gerar(LEDGER)


def test_contagens_do_paper_expandido_fecham_com_o_total():
    expandido = pn.expandir(TEX, NUMEROS_TEX)
    n = pn.numeros(LEDGER)
    k, t = int(n["NumUBKernel"]), int(n["NumCelulas"])
    assert expandido.count(f"${k}$ of the ${t}$ upper bounds") == 2  # resumo e seção do ledger
    assert f"The other ${t - k}$ upper bounds are only claimed" in expandido
    assert int(n["NumUBFormalizada"]) + int(n["NumUBReproduzida"]) == k


def test_expandir_troca_so_macro_conhecida_e_respeita_letra_seguinte():
    numeros = "\\newcommand{\\NumA}{12}\n"
    assert pn.expandir("$\\NumA$ e \\NumA{} e \\NumAB e \\NumB", numeros) == "$12$ e 12 e \\NumAB e \\NumB"


def test_secao_da_campanha_perdeu_um_marcador():
    """A segunda rodada da campanha de 2026-10-07 preenche entre marcadores; cada frente tem início e fim."""
    for frente in ("m3:superiores", "m4:exatos", "m5:lean", "m7:funsearch", "m6:cruzamento"):
        i, f = TEX.find(f"% CAMPANHA:{frente}:INICIO"), TEX.find(f"% CAMPANHA:{frente}:FIM")
        assert 0 <= i < f, frente
