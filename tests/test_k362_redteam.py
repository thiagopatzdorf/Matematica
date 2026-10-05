"""Red team de K_3(6,2) >= 16 (tools/exatos/k362/redteam, docs/exatos/k362/K3_M15_REDTEAM.md).

Os testes não dependem dos dados do PR #57 (branch ainda em rascunho): conferem as ferramentas do
red team em casos pequenos e no código conhecido de 17 palavras. A rodada sobre os 12 054
certificados está descrita no documento, com comando e resultado.
"""
import itertools
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "k362" / "redteam"))

import burnside  # noqa: E402
import farkas_min  # noqa: E402

C17 = """100112 221220 111001 122120 201021 221122 002200 021110 002102 200100 010021 122222
212011 021212 220001 200202 100210""".split()


def orbitas_forca_bruta(q, m, s):
    pts = list(itertools.product(range(q), repeat=m))
    grupo = [(perm, sims) for perm in itertools.permutations(range(m))
             for sims in itertools.product(itertools.permutations(range(q)), repeat=m)]
    vistos, classes = set(), 0
    for S in itertools.combinations(pts, s):
        if S in vistos:
            continue
        classes += 1
        for perm, sims in grupo:
            vistos.add(tuple(sorted(tuple(sims[i][p[perm[i]]] for i in range(m)) for p in S)))
    return classes


@pytest.mark.parametrize("q,m,s", [(3, 3, 2), (3, 3, 3), (3, 3, 4), (2, 4, 3), (2, 4, 4), (3, 2, 3), (2, 3, 4)])
def test_burnside_por_classes_erra_a_contagem_de_orbitas(q, m, s):
    assert burnside.orbitas(q, m, [s])[s] == orbitas_forca_bruta(q, m, s)


@pytest.mark.parametrize("s", [2, 3])
def test_configuracoes_de_z3_5_deixam_orbita_de_fora(s):
    pytest.importorskip("numpy")
    import fatia
    assert len(fatia.configuracoes(3, 5, s)) == burnside.orbitas(3, 5, [s])[s]


# Certificado à mão para K_3(4,1) <= 8, instância s* = 2: soma de todas as linhas de cobertura dá
# 9·sum z >= 81; com mu_tamanho = -9 fica 81 - 72 = 9 > 0 = max(0·z).
INST_K341 = (2, [[0, 0, 0], [1, 1, 1]], [3, 3])


def cert_k341(mu0=-9):
    return {"fixos": [], "y": {str(k): 1 for k in range(81)}, "mu": [mu0, 0, 0]}


def folga_k341(cert, M=8):
    s, K, t = INST_K341
    t = [3, M - s - 3]
    return farkas_min.folga(farkas_min.Sistema(3, 4, 1, M, s, K, t), cert)


def test_farkas_min_recusa_certificado_valido_da_cota_de_esfera():
    assert folga_k341(cert_k341()) == 9


def test_farkas_min_aceita_y_negativo():
    c = cert_k341()
    c["y"]["0"] = -1
    with pytest.raises(ValueError):
        folga_k341(c)


def test_farkas_min_aceita_certificado_sem_folga():
    assert folga_k341(cert_k341(mu0=-8)) <= 0


def test_farkas_min_aceita_certificado_no_valor_otimo_K341_igual_a_9():
    # K_3(4,1) = 9: com M = 9 a mesma combinação dá 81 - 81 = 0, que não é contradição
    assert folga_k341(cert_k341(), M=9) <= 0


def test_farkas_min_aceita_linha_de_fibra_inexistente():
    c = cert_k341()
    c["y"][str(81 + 3 * 3)] = 1  # além das (n-1)·q linhas de fibra
    with pytest.raises(ValueError):
        folga_k341(c)


def test_arvore_incompleta_passa_como_completa():
    assert farkas_min.arvore_cobre([[[5, 1]], [[5, 0], [7, 1]], [[5, 0], [7, 0]]])
    assert not farkas_min.arvore_cobre([[[5, 1]], [[5, 0], [7, 1]]])
    assert farkas_min.arvore_cobre([[]])


def test_folha_que_contradiz_a_fatia_nao_e_tratada_como_vazia():
    s, K, t = INST_K341
    sis = farkas_min.Sistema(3, 4, 1, 8, s, K, t)
    # o ponto 0000 está em K (fixo em 1); a folha z_0000 = 0 é vazia
    assert farkas_min.folga(sis, {"fixos": [[0, 0]], "y": {}, "mu": [0, 0, 0]}) is None


def _c17_normalizado(semente):
    import canon_fatia
    import codigos_reais
    cod = [tuple(map(int, w)) for w in C17]
    iso = codigos_reais.isometria_aleatoria(cod, random.Random(semente))
    return canon_fatia.normalizar(iso, 3, 6)


@pytest.mark.parametrize("semente", range(4))
def test_codigo_de_17_viola_alguma_restricao_da_propria_instancia(semente):
    import codigos_reais
    (s, K, t), norm = _c17_normalizado(semente)
    assert codigos_reais.canonica(K)
    sis = farkas_min.Sistema(3, 6, 2, 17, s, K, t)
    assert codigos_reais.viola(sis, norm) == []


def test_multiplicador_aleatorio_prova_instancia_viavel():
    """Farkas: se a instância tem solução (o próprio código de 17), nenhum (y, mu) pode passar."""
    (s, K, t), _ = _c17_normalizado(0)
    sis = farkas_min.Sistema(3, 6, 2, 17, s, K, t)
    rng = random.Random(3)
    for _ in range(40):
        y = {str(rng.randrange(729 + 15)): rng.randrange(1, 20) for _ in range(rng.randrange(1, 90))}
        mu = [rng.randrange(-30, 30) for _ in range(3)]
        g = farkas_min.folga(sis, {"fixos": [], "y": y, "mu": mu})
        assert g <= 0


def test_lemas_auxiliares_falham_no_codigo_de_17():
    pytest.importorskip("scipy")
    import codigos_reais
    assert codigos_reais.lemas([tuple(map(int, w)) for w in C17]) == []


def _lista_pequena():
    pytest.importorskip("numpy")
    import fatia
    return [[s, [list(k) for k in K], list(t)] for s, K, t in fatia.instancias(3, 5, 2, 8)]


def test_lista_de_k352_m8_tem_orbita_faltando():
    import lista_completa
    rel, n = lista_completa.conferir(3, 5, 2, 8, _lista_pequena())
    assert all(r["faltam"] == r["sobram"] == r["blocos_ruins"] == 0 for r in rel.values())


def test_lista_sem_uma_instancia_passa_como_completa():
    import lista_completa
    lista = _lista_pequena()
    assert lista
    rel, n = lista_completa.conferir(3, 5, 2, 8, lista[1:])
    assert any(r["faltam"] or r["blocos_ruins"] for r in rel.values())
