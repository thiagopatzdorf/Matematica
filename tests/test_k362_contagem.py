"""K_3(6,2), M = 15: contagem dupla, LPs agregados e certificados de Farkas por instância.

Os testes que só precisam da biblioteca padrão conferem os certificados versionados (o que
sustenta a afirmação "nenhum código de 15 palavras"): a lista de instâncias bate com o sha256
registrado, uma amostra das folhas passa no verificador exato e certificados adulterados são
recusados. Os que precisam de scipy reproduzem valores conhecidos e pulam sem ele.
"""
import gzip
import itertools
import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "tools" / "exatos" / "k362" / "contagem"
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "gaps2"))



def _mod(nome):
    """Carrega pelo caminho: há outros `verificar.py` no sys.path da suíte."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("k362_" + nome, DIR / (nome + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


verificar = _mod("verificar")

INST15 = DIR / "dados" / "K3_6_2_M15_instancias.json.gz"
CERT15 = DIR / "dados" / "K3_6_2_M15_certificados.jsonl.gz"
SHA15 = "5a07459ed8a82a18ad4169739f887c6ec77c90b24576680d40c3650a239217e6"


def _m15():
    ins = json.loads(gzip.open(INST15).read())
    regs = [json.loads(ln) for ln in gzip.open(CERT15, "rt")]
    return ins, regs


def test_lista_de_instancias_m15_bate_com_o_sha256_registrado():
    import hashlib
    assert hashlib.sha256(gzip.open(INST15).read()).hexdigest() == SHA15


def test_toda_instancia_m15_tem_registro_na_ordem_e_com_arvore_completa():
    ins, regs = _m15()
    assert len(ins) == len(regs) == 12049
    for i, (r, (s, K, t)) in enumerate(zip(regs, ins)):
        assert r["inst"] == i and [r["s"], r["K"], r["t"]] == [s, K, t] and r["folhas"]
        assert verificar.arvore_completa([f["fixos"] for f in r["folhas"]])


def test_todas_as_folhas_m15_passam_no_verificador_exato():
    """É o que sustenta "nenhum código de 15 palavras": as 12 049 instâncias, todas as folhas."""
    ins, regs = _m15()
    pts, bola = verificar.bolas(3, 6, 2)
    ruins = [i for i, r in enumerate(regs) for f in r["folhas"]
             if not verificar.folha_ok(3, 6, 15, *ins[i], pts, bola, f)]
    assert ruins == []


def test_certificado_adulterado_e_recusado():
    ins, regs = _m15()
    pts, bola = verificar.bolas(3, 6, 2)
    s, K, t = ins[0]
    f = regs[0]["folhas"][0]
    assert verificar.folha_ok(3, 6, 15, s, K, t, pts, bola, f)
    k = next(iter(f["y"]))
    tirado = dict(f, y={x: v for x, v in f["y"].items() if int(x) >= 729})  # sem as linhas de cobertura
    negativo = dict(f, y=dict(f["y"], **{k: -1}))  # foi o erro real do gerador (piso de -1e-12)
    assert not verificar.folha_ok(3, 6, 15, s, K, t, pts, bola, tirado)
    assert not verificar.folha_ok(3, 6, 15, s, K, t, pts, bola, negativo)
    s2, K2, t2 = ins[-1]  # o certificado de uma instância não serve para outra
    assert not verificar.folha_ok(3, 6, 15, s2, K2, t2, pts, bola, f)


def test_verificador_exige_sha256_da_lista_e_recusa_lista_trocada(tmp_path):
    """Sem --sha256, ou com a lista trocada, a conferência falha (ressalva L5 do red team)."""
    import subprocess
    lista = tmp_path / "i15.json"
    lista.write_bytes(gzip.open(INST15).read())
    base = [sys.executable, str(DIR / "verificar.py"), "--q", "3", "--n", "6", "--R", "2", "--M", "15",
            "--instancias", str(lista), "--certificados", str(CERT15)]
    assert subprocess.run(base, capture_output=True).returncode != 0
    assert subprocess.run(base + ["--sha256", "0" * 64], capture_output=True).returncode != 0
    ok = subprocess.run(base + ["--sha256", SHA15], capture_output=True, text=True)
    assert ok.returncode == 0 and "TODAS INVIÁVEIS" in ok.stdout
    trocada = tmp_path / "trocada.json"
    ins = json.loads(lista.read_bytes())
    ins[0], ins[1] = ins[1], ins[0]
    trocada.write_text(json.dumps(ins))
    r = subprocess.run(base[:-4] + ["--instancias", str(trocada), "--certificados", str(CERT15),
                                    "--sha256", SHA15], capture_output=True)
    assert r.returncode != 0


def test_arvore_sem_um_dos_ramos_e_recusada():
    assert verificar.arvore_completa([[[5, 1]], [[5, 0], [7, 1]], [[5, 0], [7, 0]]])
    assert not verificar.arvore_completa([[[5, 1]], [[5, 0], [7, 1]]])
    assert not verificar.arvore_completa([[[5, 1]], [[6, 0]]])


def test_perfil_equilibrado_fixa_a_soma_das_distancias_em_todo_ponto():
    """Lema: fibras todas de tamanho M/q  <=>  sum_c d(x,c) = n M (q-1)/q para todo x."""
    rng = random.Random(3)
    for _ in range(20):
        cols = [rng.sample([a for a in range(3) for _ in range(5)], 15) for _ in range(6)]
        cod = list(zip(*cols))
        for x in itertools.product(range(3), repeat=6):
            assert sum(sum(a != b for a, b in zip(x, c)) for c in cod) == 60


# ---- precisam de scipy -------------------------------------------------------------------

def test_tabelas_de_intersecao_e_capacidade_de_k362():
    pytest.importorskip("scipy")
    esferas = _mod("esferas")
    assert esferas.intersecoes(3, 6, 2) == [73, 33, 25, 12, 6, 0, 0]
    cap = esferas.capacidades(3, 6, 2)
    assert cap[1] == [12, 12, 4, 3, 0, 0, 0] and cap[3][5] == 10 and cap[6][4:] == [4, 12, 22]
    assert all(sum(cap[r][d] for r in range(7)) == 73 for d in range(7))


def test_lp_local_reproduz_k341_e_e_fraco_em_k352():
    pytest.importorskip("scipy")
    esferas = _mod("esferas")
    assert not esferas.lp_local(3, 4, 1, 8) and esferas.lp_local(3, 4, 1, 9)
    assert esferas.lp_local(3, 5, 2, 6)  # o LP local não passa de 6; K_3(5,2) = 8


@pytest.mark.parametrize("q,n,R,M,todas", [(3, 5, 2, 7, True), (2, 6, 1, 11, True), (3, 5, 2, 8, False)])
def test_pipeline_lp_reproduz_cotas_conhecidas(q, n, R, M, todas, tmp_path):
    """K_3(5,2) = 8 e K_2(6,1) = 12: M abaixo do ótimo fica todo certificado; no ótimo, não."""
    pytest.importorskip("scipy")
    certificar_lp = _mod("certificar_lp")
    import fatia
    ins = [[s, [list(k) for k in K], list(t)] for s, K, t in fatia.instancias(q, n, R, M)]
    pts, bola = verificar.bolas(q, n, R)
    ok = []
    for i, (s, K, t) in enumerate(ins):
        reg = certificar_lp._registro((q, n, R, M, i, (s, K, t)))
        ok.append(bool(reg["folhas"]) and verificar.arvore_completa([f["fixos"] for f in reg["folhas"]])
                  and all(verificar.folha_ok(q, n, M, s, K, t, pts, bola, f) for f in reg["folhas"]))
    assert all(ok) == todas


def test_codigo_de_17_palavras_deixa_sua_instancia_lp_viavel():
    """Sanidade: um código que existe nunca pode ganhar certificado de inviabilidade."""
    pytest.importorskip("scipy")
    import canon_fatia
    certificar_lp = _mod("certificar_lp")
    from test_gaps2 import C17
    (s, K, t), cod = canon_fatia.normalizar([tuple(map(int, w)) for w in C17], 3, 6)
    sis = certificar_lp.sistema(3, 6, 2, 17, s, K, t)
    assert certificar_lp._dual(*sis)[0] <= 1e-9
