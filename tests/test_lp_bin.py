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


def test_cobertura_por_walsh_hadamard_bate_com_a_soma_linha_por_linha():
    import random
    rng = random.Random(1)
    for n, R in [(5, 1), (6, 2), (7, 3)]:
        y = [rng.choice([0, 0, 1, 5, 12]) for _ in range(1 << n)]
        ingenuo = [sum(v for x, v in enumerate(y) if bin(x ^ c).count("1") <= R) for c in range(1 << n)]
        assert vbin.cobertura(n, R, y) == ingenuo


def _blocos_cli(tmp_path, *args):
    import subprocess
    r = subprocess.run([sys.executable, str(RAIZ / "tools/exatos/lp_bin/blocos_bin.py"), *args],
                       capture_output=True, text=True, cwd=tmp_path)
    return r


def test_blocos_retomados_depois_de_interrupcao_juntam_num_arquivo_que_o_verificador_aceita(tmp_path):
    """Preempção no meio: blocos já gravados são pulados, e o juntado passa em verificar_bin."""
    import hashlib
    import json
    fb = _bin()
    _cert()
    ins = fb.instancias(7, 2, 6)
    lista = tmp_path / "i.json"
    json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(lista, "w"))
    base = ["--n", "7", "--R", "2", "--M", "6", "--instancias", str(lista), "--bloco", "5"]
    # 1ª rodada só da raiz e só dos dois primeiros blocos (simula a VM caindo depois do bloco 1)
    assert _blocos_cli(tmp_path, "rodar", *base, "--dir", "raiz", "--sem-ramos", "--ate", "2").returncode == 0
    marca = (tmp_path / "raiz" / "bloco_00000.jsonl.gz").stat().st_mtime_ns
    assert _blocos_cli(tmp_path, "rodar", *base, "--dir", "raiz", "--sem-ramos").returncode == 0
    assert (tmp_path / "raiz" / "bloco_00000.jsonl.gz").stat().st_mtime_ns == marca  # não refeito
    assert _blocos_cli(tmp_path, "rodar", *base, "--dir", "ramos", "--refazer-dir", "raiz",
                       "--orcamento", "2000").returncode == 0
    r = _blocos_cli(tmp_path, "juntar", "--dir", "ramos", "--total", str(len(ins)), "--bloco", "5",
                    "--saida", "c.jsonl.gz")
    assert r.returncode == 0, r.stderr
    sha = hashlib.sha256(lista.read_bytes()).hexdigest()
    for j in ("1", "3"):
        v = subprocess_verificar(tmp_path, lista, sha, "c.jsonl.gz", j)
        assert v.returncode == 0 and "TODAS INVIÁVEIS" in v.stdout, v.stdout + v.stderr


def subprocess_verificar(tmp_path, lista, sha, cert, j="1"):
    import subprocess
    return subprocess.run([sys.executable, str(RAIZ / "tools/exatos/lp_bin/verificar_bin.py"), "--n", "7",
                           "--R", "2", "--M", "6", "--instancias", str(lista), "--certificados",
                           str(tmp_path / cert), "--sha256", sha, "-j", j], capture_output=True, text=True)


def test_verificador_paralelo_recusa_certificado_adulterado_e_fora_de_ordem(tmp_path):
    """-j só distribui as folhas: adulterar um y ou trocar a ordem continua reprovando."""
    import gzip
    import hashlib
    import json
    fb = _bin()
    cert = _cert()
    ins = fb.instancias(7, 2, 6)
    lista = tmp_path / "i.json"
    json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(lista, "w"))
    E = cert.Espaco(7, 2)
    regs = []
    for i, (s, K, t) in enumerate(json.load(open(lista))):
        folhas, modo = cert.certificar(E, 6, s, [tuple(k) for k in K], t, orc=2000)
        regs.append({"inst": i, "s": s, "K": K, "t": t, "modo": modo, "folhas": folhas})
    sha = hashlib.sha256(lista.read_bytes()).hexdigest()

    def grava(nome, rr):
        with gzip.open(tmp_path / nome, "wt") as f:
            for r in rr:
                f.write(json.dumps(r) + "\n")

    grava("bom.gz", regs)
    assert subprocess_verificar(tmp_path, lista, sha, "bom.gz", "3").returncode == 0
    ruim = json.loads(json.dumps(regs))
    f0 = ruim[5]["folhas"][0]
    f0["y"] = {k: 0 for k in f0["y"]}  # zera a combinação: a folga deixa de ser positiva
    grava("ruim.gz", ruim)
    v = subprocess_verificar(tmp_path, lista, sha, "ruim.gz", "3")
    assert v.returncode == 1 and "recusadas 1 [5]" in v.stdout, v.stdout
    grava("ordem.gz", [regs[1], regs[0]] + regs[2:])
    assert subprocess_verificar(tmp_path, lista, sha, "ordem.gz", "3").returncode == 1


def test_juntar_recusa_quando_falta_bloco(tmp_path):
    (tmp_path / "d").mkdir()
    import gzip
    with gzip.open(tmp_path / "d" / "bloco_00000.jsonl.gz", "wt") as f:
        f.write("{}\n")
    r = _blocos_cli(tmp_path, "juntar", "--dir", "d", "--total", "10", "--bloco", "5", "--saida", "x.gz")
    assert r.returncode != 0 and "faltam 1 blocos" in r.stderr and not (tmp_path / "x.gz").exists()


def test_remendos_espalhados_entre_partes_cobrem_as_vivas_e_o_juntado_passa(tmp_path):
    """Vivas da raiz (aqui simuladas apagando certificados) ramificadas em 2 partes: sem os
    remendos o juntado é recusado; com eles, aceito. Um remendo sem certificado não apaga nada."""
    import gzip
    import hashlib
    import json
    fb = _bin()
    _cert()
    ins = fb.instancias(9, 3, 6)
    lista = tmp_path / "i.json"
    json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(lista, "w"))
    base = ["--n", "9", "--R", "3", "--M", "6", "--instancias", str(lista)]
    assert _blocos_cli(tmp_path, "rodar", *base, "--dir", "raiz", "--bloco", "10", "--sem-ramos").returncode == 0
    vivas = [3, 4, 17, 25, 40]
    for k in {i // 10 for i in vivas}:  # simula vivas: apaga o certificado da raiz
        p = tmp_path / "raiz" / f"bloco_{k:05d}.jsonl.gz"
        regs = [json.loads(ln) for ln in gzip.open(p, "rt")]
        for r in regs:
            if r["inst"] in vivas:
                r["folhas"], r["modo"] = None, None
        with gzip.open(p, "wt") as f:
            f.writelines(json.dumps(r) + "\n" for r in regs)
    (tmp_path / "vivas.json").write_text(json.dumps(vivas))
    sha = hashlib.sha256(lista.read_bytes()).hexdigest()
    total = ["--total", str(len(ins)), "--bloco", "10"]

    def verif(cert):
        import subprocess
        return subprocess.run([sys.executable, str(RAIZ / "tools/exatos/lp_bin/verificar_bin.py"), "--n", "9",
                               "--R", "3", "--M", "6", "--instancias", str(lista), "--certificados",
                               str(tmp_path / cert), "--sha256", sha, "-j", "2"], capture_output=True, text=True)

    assert _blocos_cli(tmp_path, "juntar", "--dir", "raiz", *total, "--saida", "sem.gz").returncode == 0
    v = verif("sem.gz")
    assert v.returncode == 1 and "recusadas 5" in v.stdout, v.stdout
    for parte in ("0", "1"):
        r = _blocos_cli(tmp_path, "remendar", *base, "--vivas", "vivas.json", "--dir", "rem", "--grupo", "2",
                        "--parte", parte, "--partes", "2", "--orcamento", "500")
        assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in (tmp_path / "rem").glob("remendo_*.jsonl.gz")) == [
        "remendo_00000.jsonl.gz", "remendo_00001.jsonl.gz", "remendo_00002.jsonl.gz"]
    # um remendo posterior sem certificado não pode desfazer o anterior
    (tmp_path / "rem2").mkdir()
    with gzip.open(tmp_path / "rem2" / "remendo_00000.jsonl.gz", "wt") as f:
        f.write(json.dumps({"inst": 3, "folhas": None}) + "\n")
    r = _blocos_cli(tmp_path, "juntar", "--dir", "raiz", *total, "--saida", "com.gz", "--remendos", "rem", "rem2")
    assert r.returncode == 0 and "5 registros vindos de remendos" in r.stdout, r.stdout + r.stderr
    v = verif("com.gz")
    assert v.returncode == 0 and "TODAS INVIÁVEIS" in v.stdout, v.stdout
