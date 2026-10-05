"""Autópsia K_3(6,2) M=15 (tools/exatos/k362/hard6): as medidas medem a fórmula certa."""
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "exatos", "k362", "hard6"))
au = pytest.importorskip("autopsia")

INST = (5, ((0, 0, 0, 0, 0), (0, 0, 1, 1, 1), (0, 0, 2, 2, 2), (0, 1, 0, 1, 2), (0, 1, 1, 2, 0)), (5, 5))


def satisfaz(cons, a):
    for vs, op, r, _ in cons:
        s = sum(a[v] for v in vs)
        if (op == "=" and s != r) or s < r:
            return False
    return True


def test_reducao_descarta_um_codigo_que_o_opb_original_recusaria():
    """A fórmula efetiva e o OPB original dão o mesmo veredito em atribuições completas."""
    livres, cons = au.reduzir(INST)
    assert len(livres) == 486
    txt, _ = au.opb(INST)
    orig = []
    for ln in txt.splitlines()[1:]:
        t = ln.split()
        vs = [int(x[1:]) for x in t[1:-3:2]]
        orig.append((vs, t[-3], int(t[-2]), ""))
    fix = {au.VAR[c]: int(c[1:] in INST[1]) for c in au.PTS if c[0] == 0}
    rng = random.Random(7)
    for _ in range(200):
        a = dict(fix)
        esc = set(rng.sample(livres[:243], 5) + rng.sample(livres[243:], 5))
        a.update({v: int(v in esc) for v in livres})
        assert satisfaz(cons, a) == satisfaz(orig, a)


def test_cnf_do_totalizador_aceita_exatamente_o_que_a_cardinalidade_aceita():
    from pysat.solvers import Cadical153
    livres, cons = au.reduzir(INST)
    nv, cls = au.cnf(livres, cons)
    rng = random.Random(3)
    with Cadical153(bootstrap_with=cls) as s:
        for k in (8, 10, 10, 12):
            esc = set(rng.sample(livres, k))
            a = {v: int(v in esc) for v in livres}
            assume = [v if a[v] else -v for v in livres]
            assert s.solve(assumptions=assume) == satisfaz(cons, a)


def test_estabilizador_de_um_ponto_e_o_grupo_inteiro_que_fixa_a_origem():
    # S_2 wr S_5 = 2^5 * 5! = 3840 elementos fixam 00000
    assert len(au.estabilizador(((0, 0, 0, 0, 0),))) == 3840


def test_propagacao_detecta_bloco_impossivel():
    cons = [([1, 2, 3], "=", 3, "bloco"), ([1, 2], "=", 1, "bloco")]
    assert au.propagar(cons, {}) is False


def test_opb_do_cache_e_identico_ao_de_fatia_pb():
    """O censo usa o OPB com cache; um byte diferente quebraria o "subconjunto literal"."""
    for inst in (INST, (2, ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1)), (8, 5))):
        assert au.opb(inst)[0] == au.fatia_pb.opb(3, 6, 2, 15, inst)[0]


def test_empacotamento_nunca_passa_do_lp_nem_o_lp_da_cobertura_inteira():
    K = INST[1]
    assert au.nu(K) <= au.tau(K) + 1e-9 <= au.gama(K) + 1e-9


RS = os.environ.get("ROUNDINGSAT")


@pytest.mark.skipif(not RS, reason="roundingsat ausente")
def test_dura_11927_cai_no_subconjunto_da_fatia_0_em_segundos():
    """A 11927 levou 3,5 min na fórmula inteira; o subconjunto A (linhas literais) é UNSAT."""
    import subprocess
    import tempfile
    cp = pytest.importorskip("censo_projecao")
    K = tuple(tuple(int(ch) for ch in w) for w in ("00000", "00001", "11110", "11121", "22212"))
    txt, _ = au.opb((5, K, (5, 5)))
    sub = au.opb_subconjunto(txt, cp.subconjuntos(txt)["A"])
    assert set(sub.splitlines()[1:]) <= set(txt.splitlines()[1:])
    with tempfile.NamedTemporaryFile("w", suffix=".opb") as f:
        f.write(sub)
        f.flush()
        out = subprocess.run([RS, f.name, "--print-sol=0"], capture_output=True, text=True,
                             timeout=120).stdout
    assert "s UNSATISFIABLE" in out
