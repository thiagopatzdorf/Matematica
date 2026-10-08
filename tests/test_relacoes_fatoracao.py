"""Leitor das relações: a coluna é o ideal (primo e raiz), o descasque reproduz o purge do CADO e o prefixo não vaza futuro."""
import gzip
import json
import random
import shutil
import sys

import numpy as np
import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import captura_relacoes as cap  # noqa: E402
import relacoes as rel  # noqa: E402

FIXTURE = RAIZ / "tests" / "fixtures" / "fatoracao" / "captura_c30"
PURGE_VAZIO = {"inicio": {"nrows": 0, "ncols": 0, "excess": 0}, "apos_singletons": {"nrows": 0, "ncols": 0, "excess": 0},
               "final": {"nrows": 0, "ncols": 0, "excess": 0}}


def capturar(tmp_path, relacoes, livres=(), poly="n: 15\nskew: 1.0\nc0: 1\nc1: 0\nc2: 1\nY0: -3\nY1: 4\n"):
    """Captura sintética mínima. Cada relação é `(a, b, primos_lado0_hex, primos_lado1_hex)`."""
    d = tmp_path / "cap"
    d.mkdir()
    linhas = ["#ordem\tbloco\tq\trho\ta\tb\tp0\tp1"]
    for i, (a, b, p0, p1) in enumerate(relacoes):
        linhas.append(f"{i}\t0\t11\t3\t{a}\t{b}\t{p0}\t{p1}")
    with gzip.open(d / "relacoes.tsv.gz", "wt", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")
    with gzip.open(d / "livres.tsv.gz", "wt", encoding="utf-8") as fh:
        fh.write("#p\tn_indices\n" + "".join(f"{p}\t{n}\n" for p, n in livres))
    (d / "poly.txt").write_text(poly, encoding="utf-8")
    (d / "arquivos.json").write_text(json.dumps([{"nome": "x", "n_relacoes": len(relacoes), "n_sq": 1, "cpu_s": 1.0}]))
    (d / "manifest.json").write_text(json.dumps({"purge": PURGE_VAZIO}))
    return d


def test_descasque_que_nao_reproduz_o_purge_do_cado():
    r = rel.reproduz_purge_do_cado(rel.carregar(FIXTURE))
    assert r["inicio_bate"] and r["fim_bate"], r


def test_relacao_livre_de_primo_que_divide_o_coeficiente_lider_perde_a_coluna_do_infinito():
    # c30: lc(f) = 880 = 2^4 * 5 * 11; as livres de 5 e de 11 listam o ponto no infinito além das raízes finitas
    assert rel.carregar(FIXTURE).livres_discrepantes == []


def test_relacao_livre_com_p_dividindo_lc_e_sem_raiz_finita_tem_duas_colunas(tmp_path):
    poly = "n: 15\nskew: 1.0\nc0: 3\nc1: 0\nc2: 2\nY0: -3\nY1: 4\n"  # f = 2x^2 + 3, f = 1 mod 2: nenhuma raiz finita
    d = rel.carregar(capturar(tmp_path, [(1, 1, "3", "7")], livres=[(2, 2)], poly=poly))
    assert d.livres_discrepantes == [] and [int(x) for x in d.ideal_lado[d.col[d.ptr[1]:d.ptr[2]]]] == [0, 1]


BAD_C60_0 = """# bad ideals for poly1=116450222435743840-4043593796659*x-102436506738*x^2+22111700*x^3+8400*x^4
# p=2, r=2 : 2 ideals among 3 are bad
# I_2_2_1_1 # 1 2
2 1 2 1 2 -2
"""


def test_ideal_ruim_com_ramo_de_expoente_fixo_e_outro_que_acompanha_a_relacao():
    ruins = rel.ler_badideais(BAD_C60_0)
    assert ruins == {(2, 2): [(1, 2, [2, -2])]}
    assert rel.colunas_do_ideal_ruim(ruins[(2, 2)], 2, 1, 4, 2) == [(0, 2), (1, 0)]
    assert rel.colunas_do_ideal_ruim(ruins[(2, 2)], 2, 1, 4, 5) == [(0, 2), (1, 3)]


def test_relacao_fora_de_todos_os_ramos_do_ideal_ruim_nao_vira_coluna_inventada():
    ruins = rel.ler_badideais(BAD_C60_0)
    with pytest.raises(ValueError):
        rel.colunas_do_ideal_ruim(ruins[(2, 2)], 2, 1, 3, 2)  # b ímpar: não é o ponto no infinito, não cai no ramo


def test_ideal_ruim_de_expoente_par_fixo_nao_entra_na_matriz_de_paridade(tmp_path):
    d = capturar(tmp_path, [(1, 2, "3", "2,2")], poly="n: 15\nskew: 1.0\nc0: 1\nc1: 0\nc2: 2\nY0: -3\nY1: 4\n")
    (d / "badideais.txt").write_text(BAD_C60_0, encoding="utf-8")
    r = rel.carregar(d)
    alg = lambda ptr, col: [int(c) for c in col[ptr[0]:ptr[1]] if r.ideal_lado[c] == 1]  # noqa: E731
    assert len(alg(r.ptr, r.col)) == 1 and alg(r.pptr, r.pcol) == []  # existe nas ocorrências, some na paridade


def test_expoente_dividido_pela_inercia_vira_impar_e_entra_na_paridade(tmp_path):
    d = capturar(tmp_path, [(1, 3, "5", "3,3")])
    sem = rel.carregar(d)
    (d / "inercias.txt").write_text("1 3 3 2\n", encoding="utf-8")
    com = rel.carregar(d)
    alg = lambda r: [c for c in r.pcol[r.pptr[0]:r.pptr[1]] if r.ideal_lado[c] == 1]  # noqa: E731
    assert alg(sem) == [] and len(alg(com)) == 1


def test_expoente_que_nao_e_multiplo_da_inercia_nao_passa_calado(tmp_path):
    d = capturar(tmp_path, [(1, 3, "5", "3")])
    (d / "inercias.txt").write_text("1 3 3 2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        rel.carregar(d)


def test_primo_igual_com_raizes_diferentes_vira_a_mesma_coluna(tmp_path):
    # lado algébrico, p = 7: (a=2,b=1) e (a=9,b=1) têm raiz 2; (a=3,b=1) tem raiz 3
    d = rel.carregar(capturar(tmp_path, [(2, 1, "3", "7"), (9, 1, "3", "7"), (3, 1, "3", "7")], ))
    col = [set(d.col[d.ptr[i]:d.ptr[i + 1]]) for i in range(3)]
    alg = [{c for c in s if d.ideal_lado[c] == 1} for s in col]
    assert alg[0] == alg[1] and alg[0] != alg[2]
    assert d.n_ideais == 3  # o ideal racional (0, 3) é comum aos três; mais dois algébricos


def test_ponto_no_infinito_quando_p_divide_b_nao_se_confunde_com_a_raiz_zero(tmp_path):
    d = rel.carregar(capturar(tmp_path, [(5, 7, "3", "7"), (0, 1, "3", "7")]))
    a0 = {c for c in d.col[d.ptr[0]:d.ptr[1]] if d.ideal_lado[c] == 1}
    a1 = {c for c in d.col[d.ptr[1]:d.ptr[2]] if d.ideal_lado[c] == 1}
    assert a0 != a1


def test_expoente_par_entra_na_coluna_de_ocorrencia_mas_nao_na_matriz_modulo_2(tmp_path):
    d = rel.carregar(capturar(tmp_path, [(2, 1, "3,3", "7,7,b")]))  # 3^2 no lado 0, 7^2 e 11 no lado 1
    assert len(d.col) == 3 and len(d.pcol) == 1
    assert d.ideal_p[d.pcol[0]] == 11


def test_relacao_repetida_conta_como_duplicata_da_primeira(tmp_path):
    d = rel.carregar(capturar(tmp_path, [(2, 1, "3", "7"), (4, 1, "3", "b"), (2, 1, "3", "7")]))
    assert d.eh_dup.tolist() == [False, False, True] and d.unica_de.tolist() == [0, 1, 0] and d.n_unicas == 2


def test_prefixo_que_olha_o_futuro_ou_perde_as_relacoes_livres(tmp_path):
    d = rel.carregar(capturar(tmp_path, [(2, 1, "3", "7"), (2, 1, "3", "7"), (4, 1, "3", "b")], livres=[(3, 3)],
                              poly="n: 15\nskew: 1.0\nc0: 2\nc1: 0\nc2: 1\nY0: -3\nY1: 4\n"))
    ativas, u = rel.mascara_prefixo(d, 2)
    assert u == 1 and ativas.tolist() == [True, False, True]  # a duplicata não cria linha; a livre (última) sempre vale
    ativas, u = rel.mascara_prefixo(d, 3)
    assert u == 2 and ativas.tolist() == [True, True, True]


def test_raizes_do_cantor_zassenhaus_diferentes_da_forca_bruta():
    rng = random.Random(7)
    for p in (211, 487, 1009, 2003, 4099, 7919):
        for _ in range(4):
            f = [rng.randrange(p) for _ in range(rng.randrange(3, 7))] + [1 + rng.randrange(p - 1)]
            bruta = [x for x in range(p) if sum(c * pow(x, i, p) for i, c in enumerate(f)) % p == 0]
            assert rel.raizes_mod_p(f, p) == bruta, (p, f)


def _csr(linhas):
    ptr = np.concatenate([[0], np.cumsum([len(r) for r in linhas])]).astype(np.int64)
    return ptr, np.array([c for r in linhas for c in r], dtype=np.int64)


def test_descasque_que_tira_o_triangulo_junto_com_o_singleton():
    ptr, col = _csr([[0, 1], [1, 2], [2, 0], [0, 3]])  # a coluna 3 só aparece na última linha
    vivas, _ = rel.descascar(ptr, col, 4, np.ones(4, dtype=bool))
    assert vivas.tolist() == [True, True, True, False]
    assert rel.estatisticas(ptr, col, 4, vivas) == {"linhas": 3, "colunas": 3, "excesso": 0}


def test_descasque_que_depende_da_ordem_das_linhas():
    rng = random.Random(3)
    linhas = [sorted(rng.sample(range(40), rng.randrange(1, 4))) for _ in range(60)]
    ptr, col = _csr(linhas)
    base, _ = rel.descascar(ptr, col, 40, np.ones(len(linhas), dtype=bool))
    for semente in range(5):
        ordem = list(range(len(linhas)))
        random.Random(semente).shuffle(ordem)
        p2, c2 = _csr([linhas[i] for i in ordem])
        v2, _ = rel.descascar(p2, c2, 40, np.ones(len(linhas), dtype=bool))
        assert sorted(np.array(ordem)[v2]) == sorted(np.nonzero(base)[0])


def test_descasque_de_tudo_que_e_singleton_deixa_alguma_linha():
    ptr, col = _csr([[0], [1], [2]])
    vivas, _ = rel.descascar(ptr, col, 3, np.ones(3, dtype=bool))
    assert not vivas.any()


def test_nucleo_do_prefixo_vazio_so_tem_as_livres_e_o_inteiro_e_o_do_cado():
    d = rel.carregar(FIXTURE)
    vazio, _ = rel.nucleo(d, 0)
    completo, _ = rel.nucleo(d)
    assert vazio["linhas"] <= d.n_livres and completo["linhas"] > vazio["linhas"]
    assert completo["linhas"] == d.manifesto["purge"]["apos_singletons"]["nrows"]


def test_fixture_com_arquivo_adulterado_continua_com_o_sha256_do_manifesto(tmp_path):
    copia = tmp_path / "f"
    shutil.copytree(FIXTURE, copia)
    man = json.loads((copia / "manifest.json").read_text())
    assert all(cap.sha256_arquivo(copia / n) == h for n, h in man["sha256"].items())
    (copia / "poly.txt").write_text((copia / "poly.txt").read_text() + "\n")
    assert cap.sha256_arquivo(copia / "poly.txt") != man["sha256"]["poly.txt"]
