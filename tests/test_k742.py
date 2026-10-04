"""Redução de K_q(4,2) por perfis de fibras (tools/exatos/k742): completude e codificação.

O teorema "K_7(4,2) >= 18" depende de três coisas além do solver: (1) o lema das fibras, (2) a
lista de perfis cobrir todo código, (3) a quebra de simetria não perder nenhum código. Os testes
abaixo conferem (2) e (3) de forma construtiva: códigos embaralhados por elementos aleatórios
do grupo S_q wr S_4 (e ordem aleatória das palavras) são levados à forma normal e a atribuição
resultante tem de satisfazer todas as cláusulas do perfil (exceto as de cobertura, quando o
código não cobre). Nada aqui precisa de solver externo.
"""
import gzip
import itertools
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "k742"))
sys.path.insert(0, str(RAIZ / "tools" / "exatos"))

import canonizar  # noqa: E402
import encode  # noqa: E402
import lrat  # noqa: E402

N = 4


def embaralhar(cod, q, rng):
    perm = list(range(N))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(N)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(N)) for c in cod]
    rng.shuffle(out)
    return out


def checar_forma_normal(cod, q, exige_cobertura):
    M = len(cod)
    idx, norm = canonizar.canonizar(cod, q)
    perfil = encode.perfis(q, M)[idx]
    cnf, x, _ = encode.codificar(q, M, perfil)
    val = canonizar.atribuicao(cnf, x, norm, q)
    assert len(val) == cnf.nv, "variável auxiliar não ficou determinada pelas definições"
    ruins = canonizar.clausulas_violadas(cnf, val)
    if exige_cobertura:
        assert ruins == []
    else:
        # só cláusulas de cobertura (largura 6, todas positivas sobre P) podem falhar, e
        # exatamente uma por ponto descoberto (a codificação da cobertura é exata)
        assert all(len(c) == 6 and all(l > 0 for l in c) for c in ruins)
        assert len(ruins) == descobertos(norm, q) == descobertos(cod, q)
    return norm


def descobertos(cod, q):
    return sum(1 for w in itertools.product(range(q), repeat=N)
               if not any(sum(a != b for a, b in zip(w, c)) <= 2 for c in cod))


def test_lema_das_fibras_da_o_minimo_esperado():
    assert encode.fibra_minima(7, 17) == 2
    assert encode.fibra_minima(7, 18) == 2
    assert encode.fibra_minima(7, 19) == 1
    assert encode.fibra_minima(8, 22) == 2  # o passo do Florath em K_8(4,2)
    assert encode.fibra_minima(5, 10) == 1
    assert [encode.k_v31(v) for v in range(2, 9)] == [2, 5, 8, 13, 18, 25, 32]


def test_perfis_de_k7_m17_sao_os_15_multiconjuntos_dos_3_tipos():
    ts = encode.tipos(7, 17, 2)
    assert sorted(ts) == sorted([(5, 2, 2, 2, 2, 2, 2), (4, 3, 2, 2, 2, 2, 2), (3, 3, 3, 2, 2, 2, 2)])
    ps = encode.perfis(7, 17)
    assert len(ps) == 15 and len(set(ps)) == 15
    assert len(encode.perfis(7, 18)) == 70


@pytest.mark.parametrize("q", [4, 5, 7])
def test_codigo_da_particao_embaralhado_satisfaz_a_cnf_do_seu_perfil(q):
    import particao_q42 as pq

    _, parts = pq.melhor_particao(q)
    C = pq.codigo(q, parts, {p: pq.ca(p) for p in set(parts)})
    assert canonizar.cobre(C, q)
    rng = random.Random(q)
    for _ in range(3 if q == 7 else 6):
        checar_forma_normal(embaralhar(C, q, rng), q, exige_cobertura=True)


def test_codigos_aleatorios_de_17_palavras_nunca_violam_a_quebra_de_simetria():
    """Qualquer lista de 17 palavras com fibras >= 2 cai em algum perfil e satisfaz todas as
    cláusulas que não são de cobertura: a quebra de simetria não descarta código nenhum."""
    q, M = 7, 17
    rng = random.Random(2026)
    ts = encode.tipos(q, M, 2)
    for _ in range(12):
        cols = []
        for i in range(N):
            t = rng.choice(ts)
            col = [a for a, s in enumerate(t) for _ in range(s)]
            rng.shuffle(col)
            cols.append(col)
        cod = [tuple(cols[i][k] for i in range(N)) for k in range(M)]
        checar_forma_normal(embaralhar(cod, q, rng), q, exige_cobertura=False)


def test_codigo_da_particao_sem_uma_palavra_viola_uma_clausula_por_ponto_descoberto():
    import particao_q42 as pq

    q = 5
    _, parts = pq.melhor_particao(q)
    C = pq.codigo(q, parts, {p: pq.ca(p) for p in set(parts)})
    rng = random.Random(7)
    for k in range(len(C)):
        menor = C[:k] + C[k + 1:]
        if any(
                sum(1 for c in menor if c[i] == a) < encode.fibra_minima(q, len(menor))
                for i in range(N) for a in range(q)):
            continue
        assert descobertos(menor, q) > 0
        checar_forma_normal(embaralhar(menor, q, rng), q, exige_cobertura=False)


def test_verificador_lrat_python_aceita_prova_valida_e_recusa_adulterada(tmp_path):
    cnf = tmp_path / "f.cnf"
    cnf.write_text("p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n")
    prova = tmp_path / "f.lrat"
    prova.write_text("5 2 0 1 2 0\n6 0 5 3 4 0\n")
    assert lrat.verificar(str(cnf), str(prova))
    ruim = tmp_path / "g.lrat"
    ruim.write_text("5 2 0 1 0\n6 0 5 3 4 0\n")
    with pytest.raises(ValueError):
        lrat.verificar(str(cnf), str(ruim))


CERT = RAIZ / "tools" / "exatos" / "k742" / "certificados"


@pytest.mark.parametrize("cnf_gz", sorted(CERT.glob("K4_4_2_M6_p*.cnf.gz")))
def test_certificado_pequeno_k4_m6_e_conferido_pelo_verificador_python(cnf_gz):
    lr = Path(str(cnf_gz).replace(".cnf.gz", ".lrat.gz"))
    assert lrat.verificar(str(cnf_gz), str(lr))
    # e a CNF guardada é exatamente a que o codificador gera hoje
    idx = int(cnf_gz.name.split("_p")[1][:4])
    cnf, _, _ = encode.codificar(4, 6, encode.perfis(4, 6)[idx])
    guardada = [ln for ln in gzip.open(cnf_gz, "rt").read().splitlines() if not ln.startswith("c")]
    assert guardada == cnf.dimacs().splitlines()


def test_lema_das_fibras_de_k7_m18_so_precisa_de_cotas_elementares():
    assert encode.cota_elementar_31(6) == 18  # s = 1 excluído para M <= 18
    assert encode.cota_elementar_31(7) == 21  # s = 0 excluído para M <= 20
    for M in (17, 18):
        assert encode.cota_elementar_31(7) > M and encode.cota_elementar_31(6) > M - 1


def test_codigos_aleatorios_de_18_palavras_nunca_violam_a_quebra_de_simetria():
    q, M = 7, 18
    rng = random.Random(18)
    ts = encode.tipos(q, M, 2)
    for _ in range(8):
        cols = []
        for i in range(N):
            t = rng.choice(ts)
            col = [a for a, s in enumerate(t) for _ in range(s)]
            rng.shuffle(col)
            cols.append(col)
        cod = [tuple(cols[i][k] for i in range(N)) for k in range(M)]
        checar_forma_normal(embaralhar(cod, q, rng), q, exige_cobertura=False)


@pytest.mark.parametrize("jsonl", sorted(CERT.glob("K7_4_2_M1[78].jsonl")))
def test_cnf_das_rodadas_de_k7_e_a_que_o_codificador_gera_hoje(jsonl):
    import hashlib
    import json

    regs = [json.loads(ln) for ln in jsonl.read_text().splitlines()]
    q, M = regs[0]["q"], regs[0]["M"]
    assert sorted(r["perfil"] for r in regs) == list(range(len(encode.perfis(q, M))))
    assert all(r["resultado"] == "UNSAT" and r["lrat_check"] == "VERIFIED" for r in regs)
    for r in regs[:3]:
        perfil = encode.perfis(q, M)[r["perfil"]]
        cnf, _, _ = encode.codificar(q, M, perfil)
        txt = cnf.dimacs([f"K_{q}(4,2) M={M} perfil {r['perfil']}: {perfil}"])
        assert hashlib.sha256(txt.encode()).hexdigest() == r["sha256.cnf"]
