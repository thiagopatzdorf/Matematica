"""K_3(6,2), M = 16: lista da fatia mínima e certificados de Farkas por instância.

Os testes de biblioteca padrão conferem o que sustenta "nenhum código de 16 palavras": a lista
bate com o sha256 registrado e com a contagem por s*, toda instância tem registro com árvore
completa e TODAS as folhas passam no verificador exato. Os outros reproduzem a parte barata da
lista (s* <= 4, numpy) e a sanidade contra prova falsa (scipy) e pulam sem as bibliotecas.
"""
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "tools" / "exatos" / "k362" / "contagem"
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))

INST16 = DIR / "dados" / "K3_6_2_M16_instancias.json.gz"
CERT16 = DIR / "dados" / "K3_6_2_M16_certificados.jsonl.gz"
SHA16 = "3cb5b5cc47cd2b418daeaf6643ee9dd0f03c87f221f57d2f4e9cc5bb0b4f9ae7"
POR_S = {2: 18, 3: 124, 4: 1461, 5: 11071}


def _mod(nome):
    """Carrega pelo caminho: há outros `verificar.py` no sys.path da suíte."""
    spec = importlib.util.spec_from_file_location("k362_" + nome, DIR / (nome + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


verificar = _mod("verificar")


def _m16():
    ins = json.loads(gzip.open(INST16).read())
    regs = [json.loads(ln) for ln in gzip.open(CERT16, "rt")]
    return ins, regs


def test_lista_m16_bate_com_o_sha256_e_com_a_contagem_por_s():
    bruto = gzip.open(INST16).read()
    assert hashlib.sha256(bruto).hexdigest() == SHA16
    ins = json.loads(bruto)
    assert len(ins) == 12674 and Counter(s for s, _, _ in ins) == POR_S
    assert {tuple(t) for s, _, t in ins if s == 5} == {(6, 5)}


def test_toda_instancia_m16_tem_registro_na_ordem_e_com_arvore_completa():
    ins, regs = _m16()
    assert len(regs) == len(ins)
    for i, (r, (s, K, t)) in enumerate(zip(regs, ins)):
        assert r["inst"] == i and [r["s"], r["K"], r["t"]] == [s, K, t] and r["folhas"]
        assert verificar.arvore_completa([f["fixos"] for f in r["folhas"]])


def test_todas_as_folhas_m16_passam_no_verificador_exato():
    """É o que sustenta "nenhum código de 16 palavras", junto com a completude da redução."""
    ins, regs = _m16()
    pts, bola = verificar.bolas(3, 6, 2)
    ruins = [i for i, r in enumerate(regs) for f in r["folhas"]
             if not verificar.folha_ok(3, 6, 16, *ins[i], pts, bola, f)]
    assert ruins == []


def test_certificado_m16_sem_cobertura_ou_de_outra_instancia_e_recusado():
    ins, regs = _m16()
    pts, bola = verificar.bolas(3, 6, 2)
    i = next(k for k, r in enumerate(regs) if r["s"] == 5)
    s, K, t = ins[i]
    f = regs[i]["folhas"][0]
    assert verificar.folha_ok(3, 6, 16, s, K, t, pts, bola, f)
    tirado = dict(f, y={x: v for x, v in f["y"].items() if int(x) >= 729})
    assert not verificar.folha_ok(3, 6, 16, s, K, t, pts, bola, tirado)
    s2, K2, t2 = ins[-1]  # o certificado de uma instância não serve para outra
    assert not verificar.folha_ok(3, 6, 16, s2, K2, t2, pts, bola, f)


def test_subcodigos_de_16_palavras_do_codigo_de_17_caem_na_lista_e_so_violam_cobertura():
    """Completude na prática: tirar uma palavra do código de 17 dá 16 palavras que a
    normalização leva a uma instância da lista; o OPB dela só reclama de cobertura."""
    import canon_fatia
    sys.path.insert(0, str(RAIZ / "tests"))
    from test_gaps2 import C17
    lista = {(s, tuple(map(tuple, K)), tuple(t)) for s, K, t in json.loads(gzip.open(INST16).read())}
    cod = [tuple(map(int, w)) for w in C17]
    for k in range(17):
        inst, norm = canon_fatia.normalizar(cod[:k] + cod[k + 1:], 3, 6)
        assert inst in lista
        ruins = canon_fatia.restricoes_violadas(3, 6, 2, 16, inst, norm)
        assert ruins and all(ln.endswith(">= 1 ;") and ln.count(" x") == 73 for ln in ruins)


def test_parte_s_ate_4_da_lista_m16_e_reproduzida_pela_fatia():
    pytest.importorskip("numpy")
    import fatia
    ins = json.loads(gzip.open(INST16).read())
    cfg = [(s, [list(k) for k in K]) for s in range(1, 5)
           for K in fatia.configuracoes(3, 5, s, 2, (16 - s) * 11)
           if len(fatia.descobertos(3, 5, 2, K)) <= (16 - s) * 11]
    esperado = [[s, K, list(t)] for s, K in cfg for t in fatia.blocos_restantes(3, 16, s)]
    assert ins[:len(esperado)] == esperado and len(esperado) == 1603


def test_testemunha_de_17_palavras_fica_sem_certificado_com_m_17():
    """Sanidade contra prova falsa: o código de 17 do ledger não pode ser 'inviável'."""
    pytest.importorskip("scipy")
    import canon_fatia
    certificar_lp = _mod("certificar_lp")
    w = [tuple(map(int, x)) for x in (RAIZ / "tools/certificar/witnesses/K3_6_2_M17.txt").read_text().split()]
    inst, norm = canon_fatia.normalizar(w, 3, 6)
    assert canon_fatia.restricoes_violadas(3, 6, 2, 17, inst, norm) == []
    assert certificar_lp.certificar(certificar_lp.sistema(3, 6, 2, 17, *inst)) is None
