"""Códigos explícitos transcritos de artigos (data/literatura/): reconstrução e conferência exata.

O avaliador é tools/literatura/codigos_papers.py (bitset exato para binários; exaustão dos
ingredientes r-sobrejetivos e força bruta para o Corolário 3 de Kéri–Östergård 2005).
"""
import json
import sys

import pytest
from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "literatura"))
import codigos_papers as cp  # noqa: E402

CHAVES = ("ostergard_kaikkonen_1998", "ostergard_weakley_1999",
          "hamalainen_honkala_kaikkonen_litsyn_1993", "keri_ostergard_2005")
DOIS = {"ostergard_kaikkonen_1998": "10.1016/S0012-365X(97)81825-0",
        "ostergard_weakley_1999": "10.1023/A:1008326409439",
        "hamalainen_honkala_kaikkonen_litsyn_1993": "10.1007/BF01388486",
        "keri_ostergard_2005": "10.1007/s10623-004-3804-8"}


def test_toda_transcricao_cita_o_artigo_com_doi_e_o_lugar_de_cada_item():
    for ch in CHAVES:
        J = cp.carregar(ch)
        assert J["citacao"]["doi"] == DOIS[ch]
        assert J["citacao"]["autores"] and J["citacao"]["titulo"] and J["citacao"]["paginas"]
        for it in J["itens"]:
            assert it.get("local"), (ch, it["id"])
    assert not list((RAIZ / "data" / "literatura").rglob("*.pdf")), "PDF de artigo não vai para o repo"


def _binarios(nmax):
    for ch in CHAVES[:3]:
        for r in cp.reconstruir_binarios(ch):
            if r["n"] <= nmax:
                yield r


def test_todo_codigo_binario_dos_artigos_tem_o_tamanho_e_o_raio_anunciados_salvo_o_19_320_4():
    vistos = 0
    for r in _binarios(24):
        assert len(set(r["palavras"])) == len(r["palavras"]) == r["M"], r["id"]
        desc = cp.raio_ok_binario(r["palavras"], r["n"], r["R"])
        if r["id"] == "OK98-T1d":
            assert desc > 0
        else:
            assert desc == 0, (r["id"], desc)
        vistos += 1
    assert vistos >= 27


def test_o_19_320_4_da_tabela_1_transcrito_exatamente_tem_raio_5_e_o_19_6_do_exemplo_5_raio_6():
    """Achado: a Tabela 1 de Östergård–Kaikkonen 1998 (p. 167) anuncia (19,320)4 e o Exemplo 5
    diz que a matriz A é verificação de um [19,6]5. Transcrito da página, o código deixa 12 032
    pontos a distância 5 e o [19,6] tem raio 6. Nenhuma troca de um dígito hexadecimal (em M ou
    em S) baixa o raio para 4 (conferido na investigação; não repetido aqui por custo)."""
    ok = {r["id"]: r for r in cp.reconstruir_binarios("ostergard_kaikkonen_1998")}
    r = ok["OK98-T1d"]
    assert cp.raio_ok_binario(r["palavras"], 19, 4) == 12032
    assert cp.raio_ok_binario(r["palavras"], 19, 5) == 0
    it = r["item"]
    lin = cp.matriz(19, 13, cp.hexs(it["colunas_M"]), [0])
    assert len(lin) == 64
    assert cp.raio_ok_binario(lin, 19, 5) > 0 and cp.raio_ok_binario(lin, 19, 6) == 0


def test_codigo_do_osterg_weakley_e_704_palavras_de_raio_1_e_o_exemplo_n6_tem_12():
    ow = {r["id"]: r for r in cp.reconstruir_binarios("ostergard_weakley_1999")}
    assert len(ow["OW99-D"]["palavras"]) == 704 and cp.raio_ok_binario(ow["OW99-D"]["palavras"], 13, 1) == 0
    assert cp.raio_ok_binario(ow["OW99-D"]["palavras"], 13, 0) > 0
    assert len(ow["OW99-Ex6"]["palavras"]) == 12


def test_avaliador_binario_reprova_codigo_sem_uma_palavra():
    ok = {r["id"]: r for r in cp.reconstruir_binarios("ostergard_kaikkonen_1998")}
    pal = ok["OK98-T1c"]["palavras"]
    assert cp.raio_ok_binario(pal, 17, 3) == 0
    assert cp.raio_ok_binario(pal[1:], 17, 3) > 0


def test_exemplo_3_do_keri_ostergard_e_3_sobrejetivo_e_e_o_ingrediente_7_7_3():
    J = cp.carregar("keri_ostergard_2005")
    ex3 = next(i for i in J["itens"] if i["id"] == "KO05-Ex3")
    import itertools
    G = ex3["geradores_Z7"]
    pal = sorted({tuple(sum(a * g[j] for a, g in zip(m, G)) % 7 for j in range(7))
                  for m in itertools.product(range(7), repeat=3)})
    assert len(pal) == 343 and cp.e_surjetivo(pal, 7, 7, 3)
    assert sorted(cp.ler_surjetivo(7, 7, 3, 343)) == pal


def test_todo_ingrediente_versionado_e_sobrejetivo_e_o_avaliador_reprova_linha_a_menos():
    arqs = sorted((RAIZ / "data" / "literatura" / "surjetivos").glob("ca_t*_n*_v*_N*.txt"))
    assert len(arqs) >= 14
    for p in arqs:
        t, n, v, N = (int(x[1:]) for x in p.stem[3:].split("_"))
        pal = cp.ler_surjetivo(v, n, t, N)
        assert len(pal) == N and cp.e_surjetivo(pal, v, n, t), p.name
    pal = cp.ler_surjetivo(6, 4, 2, 37)
    assert not cp.e_surjetivo(pal[1:], 6, 4, 2)


@pytest.mark.parametrize("v,n,t", [(4, 5, 3), (8, 5, 3), (9, 7, 4), (16, 5, 2), (11, 7, 4)])
def test_reed_solomon_estendido_e_t_sobrejetivo(v, n, t):
    assert cp.e_surjetivo(cp.surjetivo_mds(v, n, t), v, n, t)


def test_corolario_3_reproduz_cada_celula_de_chave_n_marcada_no_json():
    J = cp.carregar("keri_ostergard_2005")
    itens = [i for i in J["itens"] if i["tipo"] == "corolario3"]
    assert len(itens) == 85
    for it in itens:
        cod = cp.corolario3(it["q"], it["n"], it["R"])
        assert cod["M"] == it["M"] and cod["partes"] == it["partes"], it["id"]
        assert sum(cod["partes"]) == it["q"] and len(cod["partes"]) == cod["k"]
        assert cod["k"] * (cod["t"] - 1) < it["n"]


@pytest.mark.parametrize("q,n,R", [(6, 5, 2), (7, 5, 2), (6, 6, 4), (6, 7, 4), (7, 7, 5), (13, 4, 2)])
def test_corolario_3_cobre_por_forca_bruta(q, n, R):
    cod = cp.corolario3(q, n, R)
    assert cp.cobre_forca_bruta(cod["palavras"], q, n, R)
    assert not cp.cobre_forca_bruta(cod["palavras"][1:], q, n, R)


def test_codigos_dos_artigos_em_data_codes_sao_os_reconstruidos():
    ours = json.loads((RAIZ / "ledger" / "ours.json").read_text())["cells"]
    vistos, feitos = 0, set()
    for L in cp.relatorio(False, nmax_bin=20, conferir_ko=False):
        p = RAIZ / "data" / "codes" / f"q{L['q']}_n{L['n']}_R{L['R']}_M{L['M']}.txt"
        e = ours.get(f"{L['q']},{L['n']},{L['R']}", {})
        reg = e.get("ours_computational") or e.get("ours_lean") or {}
        if reg.get("file") != str(p.relative_to(RAIZ)) or not p.exists() or p in feitos:
            continue  # o primeiro item que dá a célula é o gravado (K2(12,3): Exemplo 13 antes do HHKL)
        feitos.add(p)
        txt = sorted(cp.texto_palavra(w, L["q"]) for w in L["tuplas"])
        assert p.read_text().split() == txt, p.name
        vistos += 1
    assert vistos >= 20


def test_lean_gerado_cobre_exatamente_as_celulas_que_o_gerador_escolhe_e_o_ledger_registra():
    sys.path.insert(0, str(RAIZ / "tools" / "literatura"))
    import gerar_lean as gl
    teoremas, ings = gl.ko05(False)
    ko05 = (RAIZ / "CoveringLean" / "Literatura" / "KO05.lean").read_text()
    nomes = {f"K{q}_{n}_{R}_le_{M}" for q, n, R, _t, M, _p in teoremas}
    assert len(nomes) == 79 and all(f"theorem {x} :" in ko05 for x in nomes)
    for nm in ings:
        assert (RAIZ / "CoveringLean" / "Literatura" / f"Surj_{nm}.lean").exists(), nm
    ours = json.loads((RAIZ / "ledger" / "ours.json").read_text())["cells"]
    decs = {e["ours_lean"]["declaration"] for e in ours.values() if e.get("ours_lean")}
    assert {f"CoveringLit.{x}" for x in nomes} <= decs
    for p in (RAIZ / "CoveringLean" / "Literatura").glob("*.lean"):
        t = p.read_text()
        assert "sorry" not in t and "native_decide" not in t, p.name
