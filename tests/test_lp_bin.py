"""Fatia mínima binária + LP reduzido por simetria (tools/exatos/lp_bin, docs/exatos/LP_FATIA_BINARIO.md).

O que sustenta uma afirmação "nenhum código de M palavras": (1) a lista binária tem uma
configuração por classe de isometria (conferida contra a enumeração do GAPS2), (2) os
certificados gravados são do sistema completo e passam no verificador exato de
`tools/exatos/k362/contagem/verificar.py`, que não sabe nada da redução por simetria, e
(3) um código que existe nunca ganha certificado.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))
WIT = RAIZ / "tools" / "certificar" / "witnesses"


def _mod(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _bin():
    pytest.importorskip("numpy")
    return _mod("tools/exatos/lp_bin/fatia_bin.py", "lpbin_fatia")


def _cert():
    pytest.importorskip("scipy")
    return _mod("tools/exatos/lp_bin/certificar_bin.py", "lpbin_cert")


verificar = _mod("tools/exatos/k362/contagem/verificar.py", "lpbin_verificar")
vbin = _mod("tools/exatos/lp_bin/verificar_bin.py", "lpbin_vbin")


@pytest.mark.parametrize("m,s", [(3, 2), (4, 3), (5, 3), (5, 4), (6, 4), (5, 5), (3, 6)])
def test_lista_binaria_tem_uma_configuracao_por_classe_como_o_gaps2(m, s):
    fb = _bin()
    import fatia
    C, pats = fb.canonicos(m, s)
    nossas = {fatia.forma(fb.pontos(c, pats, s)) for c in C}
    deles = {fatia.forma(K) for K in fatia.configuracoes(2, m, s)}
    assert len(nossas) == len(C) and nossas == deles


@pytest.mark.parametrize("n,R,M", [(7, 2, 6), (6, 1, 11), (9, 3, 6)])
def test_instancias_binarias_sao_as_mesmas_classes_do_gaps2(n, R, M):
    fb = _bin()
    import fatia
    chave = lambda s, K, t: (s, fatia.forma(list(K)) if s else (), tuple(t))  # noqa: E731
    assert sorted(chave(*i) for i in fb.instancias(n, R, M)) == sorted(chave(*i) for i in fatia.instancias(2, n, R, M))


def _ler(nome):
    return [tuple(int(ch) for ch in ln.strip()) for ln in open(WIT / nome) if ln.strip() and not ln.startswith("#")]


@pytest.mark.parametrize("n,R,M", [(7, 2, 6), (9, 3, 6), (6, 1, 11)])
def test_abaixo_do_otimo_todo_certificado_passa_no_verificador_exato(n, R, M):
    fb, cb = _bin(), _cert()
    E = cb.Espaco(n, R)
    pts, bola = verificar.bolas(2, n, R)
    for s, K, t in fb.instancias(n, R, M):
        K, t = [list(k) for k in K], list(t)
        folhas, modo = cb.certificar(E, M, s, [tuple(k) for k in K], t)
        assert folhas and vbin.arvore([vbin.no_da_folha(f) for f in folhas])
        assert all(vbin.folha_ok(n, R, M, s, K, t, f) for f in folhas)
        if modo == "reduzido":  # folha única sem ramos: o verificador do K3(6,2) também aceita
            assert all(verificar.folha_ok(2, n, M, s, K, t, pts, bola, f) for f in folhas)


def test_certificado_de_outra_instancia_e_recusado():
    fb, cb = _bin(), _cert()
    ins = fb.instancias(7, 2, 6)
    E = cb.Espaco(7, 2)
    pts, bola = verificar.bolas(2, 7, 2)
    (s0, K0, t0), (s1, K1, t1) = ins[0], ins[-1]
    folhas, _ = cb.certificar(E, 6, s0, list(K0), list(t0))
    assert not verificar.folha_ok(2, 7, 6, s1, [list(k) for k in K1], list(t1), pts, bola, folhas[0])
    assert not vbin.folha_ok(7, 2, 6, s1, [list(k) for k in K1], list(t1), folhas[0])
    sem_cobertura = dict(folhas[0], y={k: v for k, v in folhas[0]["y"].items() if int(k) >= 1 << 7})
    assert not vbin.folha_ok(7, 2, 6, s0, [list(k) for k in K0], list(t0), sem_cobertura)


def test_ramificacao_agregada_fecha_instancia_que_a_raiz_nao_fecha_e_o_verificador_aceita():
    """K_2(10,3), M = 11, instância 7 da lista: LP viável na raiz; a ramificação em somas de
    órbitas fecha com 14 folhas, e uma árvore incompleta é recusada."""
    cb = _cert()
    s, K, t = 2, [tuple(map(int, "000000000")), tuple(map(int, "001111111"))], (9,)  # índice 7 da lista
    E = cb.Espaco(10, 3)
    assert cb.certificar(E, 11, s, list(K), list(t), ramos=False)[0] is None
    folhas, modo = cb.certificar(E, 11, s, list(K), list(t))
    assert modo == "agregado" and len(folhas) > 1
    K = [list(k) for k in K]
    assert vbin.arvore([vbin.no_da_folha(f) for f in folhas])
    assert all(vbin.folha_ok(10, 3, 11, s, K, list(t), f) for f in folhas)
    assert not vbin.arvore([vbin.no_da_folha(f) for f in folhas[1:]])


@pytest.mark.parametrize("arq,n,R", [("K2_7_2_M7.txt", 7, 2), ("K2_9_3_M7.txt", 9, 3), ("K2_8_2_M12.txt", 8, 2),
                                     ("K2_6_1_M12.txt", 6, 1)])
def test_codigo_otimo_conhecido_nunca_ganha_certificado(arq, n, R):
    _bin()
    cb = _cert()
    import canon_fatia
    cod = _ler(arq)
    (s, K, t), _ = canon_fatia.normalizar(cod, 2, n)
    folhas, _ = cb.certificar(cb.Espaco(n, R), len(cod), s, [tuple(k) for k in K], list(t), ramos=False)
    assert folhas is None


@pytest.mark.parametrize("arq,n,R", [("K2_7_2_M7.txt", 7, 2), ("K2_9_3_M7.txt", 9, 3)])
def test_codigo_que_cobre_sob_isometrias_cai_numa_instancia_da_lista(arq, n, R):
    """Completude na prática: um código de raio R, embaralhado por isometrias, normaliza para
    uma instância da lista de M = |C| (um subcódigo que não cobre pode cair fora do filtro)."""
    import random
    fb = _bin()
    import canon_fatia
    import fatia
    cod = _ler(arq)
    lista = {(s, fatia.forma(list(K)) if s else (), tuple(t)) for s, K, t in fb.instancias(n, R, len(cod))}
    rng = random.Random(7)
    for _ in range(5):
        perm, flip = rng.sample(range(n), n), [rng.randrange(2) for _ in range(n)]
        c2 = [tuple(w[perm[j]] ^ flip[j] for j in range(n)) for w in cod]
        (s, K, t), _ = canon_fatia.normalizar(c2, 2, n)
        assert (s, fatia.forma(list(K)) if s else (), tuple(t)) in lista
