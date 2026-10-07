"""Red team independente de K_4(7,4) >= 10 e K_4(6,3) >= 12 (docs/exatos/REDTEAM_K474_K463.md).

Cada teste carrega uma falha que a revisão procurou (e, onde há um mutante, prova que o teste a pegaria).
Os scripts independentes estão em `tools/exatos/fibras_redteam_k474/` e não usam o canonizador do repo.
Os testes que precisam de SAT usam `pysat` e pulam sem ele (o CI de testes não o instala; rode com
`python3 -m pip install python-sat`).
"""
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
RT = RAIZ / "tools" / "exatos" / "fibras_redteam_k474"
FIB = RAIZ / "tools" / "exatos" / "fibras"
CERT = FIB / "certificados"
for p in (str(RT), str(FIB)):
    if p not in sys.path:
        sys.path.insert(0, p)

import fib_encode as enc  # noqa: E402
import lema1_construcao as lema1  # noqa: E402
import perfis_cubos as pc  # noqa: E402


# ---------------------------------------------------------------- Lema 1 (fibras)

def test_lema1_aplicado_a_codigos_que_cobrem_deixa_a_imagem_cobrindo_com_raio_menor():
    """A construção da prova (S_i fora de A_i, phi_i) tem de dar um código de raio R-1 com <= M-s palavras."""
    falhas = lema1.principal(semente=11, por_celula=2, celulas=[(4, 4, 2), (3, 6, 3), (5, 5, 3)])
    assert falhas == 0


def test_lema1_com_s_i_que_ignora_a_i_e_pego_pela_mesma_checagem():
    """Poder do teste: se S_i pudesse cruzar A_i (erro da prova), a imagem deixaria pontos descobertos."""
    falhas = lema1.principal(semente=7, por_celula=6, mutante=True, celulas=[(4, 4, 2), (3, 6, 3)])
    assert falhas > 0


def _codigos_do_repo():
    for arq in sorted((RAIZ / "data" / "codes").glob("q*_n*_R*_M*.txt")):
        q, n, R, M = (int(p[1:]) for p in arq.stem.split("_"))
        if R <= n - 2 and q ** n <= 300_000 and M <= 40:
            cod = [tuple(int(c, 36) for c in ln.strip()) for ln in arq.read_text().splitlines()
                   if ln.strip() and not ln.startswith("#")]
            if len(cod) == M and all(len(w) == n for w in cod):
                yield arq.name, q, n, R, cod


def test_nenhuma_fibra_de_codigo_real_do_repo_fica_abaixo_do_s_min_do_lema():
    """Direção do lema: todo código REAL do repo (que cobre) tem toda fibra >= fibra_minima(q,n,R,M)."""
    vistos = 0
    for nome, q, n, R, cod in _codigos_do_repo():
        try:
            smin = enc.fibra_minima(q, n, R, len(cod))
        except KeyError:
            continue
        menor = min(sum(1 for w in cod if w[i] == a) for i in range(n) for a in range(q))
        assert menor >= smin, f"{nome}: fibra {menor} < s_min {smin}"
        # e a construção do lema funciona em cada fibra pequena desse código real
        rng = random.Random(1)
        P = lema1.pontos(q, n)
        assert lema1.descobertos(cod, q, n, R, P) == 0, f"{nome} não cobre"
        for i in range(n):
            for a in range(q):
                r = lema1.lema1(cod, q, n, R, i, a, rng)
                if r is not None:
                    s, img = r
                    assert len(img) <= len(cod) - s and lema1.descobertos(img, q - s, n - 1, R - 1) == 0, nome
        vistos += 1
    assert vistos >= 3


def test_codigo_de_10_palavras_de_k4_7_4_cobre_z4_7_com_raio_4_pela_definicao_de_distancia():
    cod = [tuple(int(c) for c in ln.strip()) for ln in
           (RAIZ / "data" / "codes" / "q4_n7_R4_M10.txt").read_text().splitlines() if ln.strip()]
    assert len(cod) == len(set(cod)) == 10
    assert lema1.descobertos(cod, 4, 7, 4) == 0


# ---------------------------------------------------------------- dependências numéricas

def _esfera(v, m, r):
    import math
    return -(-v ** m // sum(math.comb(m, k) * (v - 1) ** k for k in range(r + 1)))


def test_s_min_das_duas_celulas_depende_so_da_exclusao_da_fibra_vazia_e_de_cotas_que_o_ledger_declara():
    """Só a exclusão de s = 0 sustenta as provas: K_4(5,2) > 11 (célula (6,3)) e K_4(6,3) > 9 (célula (7,4))."""
    # cotas do ledger usadas hoje
    assert enc.cota_inferior(4, 5, 2) >= 12
    assert enc.cota_inferior(4, 6, 3) >= 10
    assert enc.fibra_minima(4, 6, 3, 11) == enc.fibra_minima(4, 7, 4, 9) == 1
    assert pc.s_min(4, 6, 3, 11) == pc.s_min(4, 7, 4, 9) == 1
    # a cota de esferas SOZINHA não basta para K_4(6,3), M = 11 (precisa de K_4(5,2) >= 12, que é literatura/CLAIMED
    # ou o cálculo K4_5_2_M11 do red team): sem ela s_min cairia para 0 e as 8008 instâncias seriam outras
    assert _esfera(4, 5, 2) == 10 and _esfera(4, 6, 3) == 6
    so_esferas = {(4, 5, 2): (_esfera(4, 5, 2), "esfera"), (4, 4, 1): (_esfera(4, 4, 1), "esfera"),
                  (3, 5, 2): (_esfera(3, 5, 2), "esfera"), (3, 6, 3): (_esfera(3, 6, 3), "esfera"),
                  (4, 6, 3): (_esfera(4, 6, 3), "esfera")}
    assert pc.s_min(4, 6, 3, 11, so_esferas) == 0
    assert pc.s_min(4, 7, 4, 9, so_esferas) == 0
    # mas para K_4(6,3), M = 9 a esfera basta (10 > 9): o "∄ 9" é elementar e dá K_4(6,3) >= 10 sem literatura
    assert pc.s_min(4, 6, 3, 9, so_esferas) == 1


def test_contagem_de_perfis_e_a_do_lema_para_as_duas_celulas():
    assert enc.contar_instancias(4, 7, 9, 7, 1) == (6, 792)
    assert enc.contar_instancias(4, 6, 11, 6, 1) == (11, 8008)
    assert len(pc.tipos(4, 9, 1)) == 6 and len(pc.tipos(4, 11, 1)) == 11


# ---------------------------------------------------------------- certificado: perfis e cubos

def test_certificado_de_k4_7_4_cobre_cada_um_dos_792_perfis_uma_vez_e_os_cubos_cobrem_a_coordenada_1():
    r = pc.verificar(CERT / "K4_7_4_M9.jsonl.xz", 4, 7, 4, 9, imprimir=False)
    assert (r["perfis"], r["inteiros"], r["perfis_em_cubos"], r["cubos"]) == (792, 786, 6, 168)


def test_certificado_de_k4_6_3_cobre_cada_um_dos_8008_perfis_uma_vez_e_os_cubos_cobrem_a_coordenada_1():
    r = pc.verificar(CERT / "K4_6_3_M11.jsonl.xz", 4, 6, 3, 11, imprimir=False)
    assert (r["perfis"], r["inteiros"], r["perfis_em_cubos"], r["cubos"]) == (8008, 7990, 18, 2100)


@pytest.mark.parametrize("nome,q,n,R,M", [("K4_7_4_M9", 4, 7, 4, 9), ("K4_6_3_M11", 4, 6, 3, 11)])
def test_cnf_regenerada_de_registros_sorteados_bate_o_sha256_e_tipos_batem_a_instancia(nome, q, n, R, M):
    import json
    import lzma
    import fecha_perfis as fp
    regs = [json.loads(ln) for ln in lzma.open(CERT / f"{nome}.jsonl.xz", "rt")]
    smin = enc.fibra_minima(q, n, R, M)
    listas = {o: enc.instancias(q, n, M, n, smin, ordem=o)[1] for o in ("min", "max")}
    for r in regs:
        pref = listas[r["ordem"]][r["inst"]]
        assert ["".join(map(str, t)) for t in pref] == r["tipos"], "campo `tipos` não é a instância `inst`"
    rng = random.Random(20261007)
    amostra = rng.sample([r for r in regs if not r.get("L")], 3) + rng.sample([r for r in regs if r.get("L")], 1)
    for r in amostra:
        assert fp.sha_cnf(q, n, M, n, smin, r, R) == r["sha256.cnf"]


# ---------------------------------------------------------------- testes que precisam de SAT

def _pysat():
    return pytest.importorskip("pysat")


def test_cubos_cobrem_todo_modelo_da_cnf_na_coordenada_1_dos_perfis_em_cubos_de_k4_7_4():
    _pysat()
    import cubos_cnf
    import json
    import lzma
    regs = [json.loads(ln) for ln in lzma.open(CERT / "K4_7_4_M9.jsonl.xz", "rt")]
    por = {}
    for r in regs:
        if r.get("L"):
            por.setdefault(r["inst"], []).append(r)
    assert len(por) == 6
    for inst, rs in por.items():
        pref = tuple(tuple(int(c) for c in s) for s in rs[0]["tipos"])
        proj = cubos_cnf.projetados(4, 7, 4, 9, pref, 1)
        grav = {tuple(int(c) for c in r["cubo"]) for r in rs}
        assert proj and all(v[:9] in grav for v in proj), f"inst {inst}: modelo fora de todo cubo"


def test_cnf_real_aponta_exatamente_os_pontos_descobertos_em_tamanho_real(monkeypatch):
    _pysat()
    import cobertura_pontual
    for q, n, R, M in ((4, 6, 3, 11), (4, 7, 4, 9)):
        monkeypatch.setattr(sys, "argv", ["x", str(q), str(n), str(R), str(M), "2", "13"])
        cobertura_pontual.main()      # levanta AssertionError se a CNF e a definição divergirem


def test_orbita_por_sat_de_codigos_sorteados_nao_perde_nenhum_e_pega_o_mutante_h_nos_dois_sentidos():
    _pysat()
    import orbita_indep as oi
    import orbita_massa as om
    rng = random.Random(3)
    q, n, R, M = 4, 4, 2, 10
    codigos = []
    smin0 = enc.fibra_minima(q, n, R, M)
    _, ins = enc.instancias(q, n, M, n, smin0)
    for _ in range(12):
        codigos.append(oi.codigo_com_perfil(q, n, list(rng.choice(ins)), rng))
    mutante = om.carregar("h_ambos")
    controle = [oi.orbita_sat(enc, q, n, M, R, c, "max", com_cobertura=False) for c in codigos]
    assert all(controle), "a CNF com quebra perde um código: quebra de simetria incompleta"
    assert not all(oi.orbita_sat(mutante, q, n, M, R, c, "max", com_cobertura=False) for c in codigos), \
        "o teste de órbita não pega (h) imposta nos dois sentidos: sem poder"


@pytest.mark.parametrize("q,n,R,M,semente", [(4, 7, 4, 9, 5), (4, 6, 3, 11, 6)])
def test_orbita_por_sat_nas_celulas_alvo_nao_perde_codigo_com_perfil_sorteado(q, n, R, M, semente):
    _pysat()
    import orbita_indep as oi
    rng = random.Random(semente)
    smin = enc.fibra_minima(q, n, R, M)
    _, ins = enc.instancias(q, n, M, n, smin)
    for _ in range(3):
        cod = oi.codigo_com_perfil(q, n, list(rng.choice(ins)), rng)
        for ordem in ("min", "max"):
            assert oi.orbita_sat(enc, q, n, M, R, cod, ordem, com_cobertura=False)


@pytest.mark.parametrize("q,n,R,M", [(3, 4, 1, 9), (3, 5, 2, 8), (3, 6, 3, 6), (4, 4, 2, 7)])
def test_codificacao_independente_da_cobertura_concorda_com_a_de_tuplas_nas_celulas_pequenas(q, n, R, M, monkeypatch):
    _pysat()
    import diferencial
    monkeypatch.setattr(sys, "argv", ["x", str(q), str(n), str(R), str(M), "10", "1"])
    with pytest.raises(SystemExit) as e:
        diferencial.main()
    assert e.value.code == 0, "as duas codificações divergem em algum caso (SAT x UNSAT)"


def test_lema1_nao_deixa_o_sat_achar_codigo_de_7_palavras_para_k4_4_2_com_fibra_vazia():
    """K_4(3,1) = 8 > 7 (calculado aqui por SAT): o lema exclui fibra vazia em K_4(4,2), M = 7."""
    _pysat()
    import lema1_sat
    assert lema1_sat.exato(4, 3, 1) == 8 and lema1_sat.exato(3, 4, 1) == 9
    assert lema1_sat.consulta(4, 4, 2, 7, 0) is False


def test_cnf_completa_aceita_o_codigo_real_de_10_palavras_de_k4_7_4_na_orbita():
    """Controle de SAT em tamanho real (cobertura por triplas + (a)-(h)): um código que cobre não pode ser perdido."""
    _pysat()
    import orbita_indep as oi
    cod = [tuple(int(c) for c in ln.strip()) for ln in
           (RAIZ / "data" / "codes" / "q4_n7_R4_M10.txt").read_text().splitlines() if ln.strip()]
    assert oi.orbita_sat(enc, 4, 7, len(cod), 4, cod, "max", com_cobertura=True)


# ---------------------------------------------------------------- o verificador de cobertura de perfis tem poder

def _fecha(tmp_path, regs, q, n, R, M):
    import json
    import subprocess
    arq = tmp_path / "x.jsonl"
    arq.write_text("".join(json.dumps(r) + "\n" for r in regs))
    r = subprocess.run([sys.executable, str(FIB / "fecha_perfis.py"), "--q", str(q), "--n", str(n), "--R", str(R),
                        "--M", str(M), str(arq)], capture_output=True, text=True)
    return r.returncode, r.stdout


def _regs(nome):
    import json
    import lzma
    return [json.loads(ln) for ln in lzma.open(CERT / f"{nome}.jsonl.xz", "rt")]


def test_fecha_perfis_reprova_certificado_sem_um_perfil_inteiro_ou_sem_um_cubo_ou_com_lrat_falho(tmp_path):
    regs = _regs("K4_7_4_M9")
    inteiros = [r for r in regs if not r.get("L")]
    cubos = [r for r in regs if r.get("L")]
    assert _fecha(tmp_path, regs, 4, 7, 4, 9)[0] == 0
    rc, out = _fecha(tmp_path, [r for r in regs if r is not inteiros[7]], 4, 7, 4, 9)
    assert rc == 1 and "1 faltando" in out, "perfil removido não foi notado"
    rc, out = _fecha(tmp_path, [r for r in regs if r is not cubos[5]], 4, 7, 4, 9)
    assert rc == 1 and "1 faltando" in out, "cubo removido não foi notado"
    ruim = [dict(r) for r in regs]
    ruim[10]["lrat_check"] = "FALHOU"
    assert _fecha(tmp_path, ruim, 4, 7, 4, 9)[0] == 1, "lrat-check que falhou foi contado como fechado"


def test_registro_com_tipos_trocados_e_pego_pela_checagem_de_coerencia_que_fecha_perfis_nao_faz():
    """fecha_perfis confia no campo `tipos`; só a comparação com a lista de instâncias pega a troca."""
    regs = _regs("K4_7_4_M9")
    assert pc.registros_incoerentes(regs, 4, 7, 4, 9) == []
    ruim = [dict(r) for r in regs]
    ints = [k for k, r in enumerate(ruim) if not r.get("L")]
    i = ints[0]
    j = next(k for k in ints if ruim[k]["tipos"] != ruim[i]["tipos"])
    ruim[i]["tipos"] = ruim[j]["tipos"]
    assert len(pc.registros_incoerentes(ruim, 4, 7, 4, 9)) == 1
    ruim = [dict(r) for r in regs]
    ruim[ints[5]]["inst"] = ruim[ints[5]]["inst"] + 1
    assert pc.registros_incoerentes(ruim, 4, 7, 4, 9) != []


# ---------------------------------------------------------------- ledger e consistência global

@pytest.mark.parametrize("q,n,R,nome", [(4, 7, 4, "K4_7_4_M9"), (4, 6, 3, "K4_6_3_M11")])
def test_ledger_declara_a_mesma_contagem_e_o_mesmo_sha256_do_certificado(q, n, R, nome):
    import hashlib
    import json
    cel = next(c for c in json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
               if (c["q"], c["n"], c["R"]) == (q, n, R))
    cert = cel["certification"]["lb"]["provenance"]["certificado"]
    regs = _regs(nome)
    assert cert["contagem"]["linhas_registro"] == len(regs)
    assert cert["contagem"]["cubos"] == sum(1 for r in regs if r.get("L"))
    assert cert["contagem"]["perfis_inteiros"] == sum(1 for r in regs if not r.get("L"))
    for arq, sha in cert["arquivos"].items():
        assert hashlib.sha256((RAIZ / arq).read_bytes()).hexdigest() == sha


def test_cotas_do_ledger_nao_contradizem_as_desigualdades_elementares_entre_celulas():
    import consistencia_ledger as cl
    L = cl.carregar()
    assert L[(4, 7, 4)] == (10, 10) and L[(4, 6, 3)][0] >= 12
    assert cl.contradicoes(L) == []
    # poder: um lb de K_4(6,3) acima de K_4(5,2) <= 16 (anexar coordenada livre) tem de ser pego
    ruim = dict(L)
    ruim[(4, 6, 3)] = (17, L[(4, 6, 3)][1])
    assert cl.contradicoes(ruim) != []


# ---------------------------------------------------------------- dependência de base recalculada aqui

@pytest.mark.parametrize("nome,q,n,R,M,perfis", [("K4_5_2_M11", 4, 5, 2, 11, 3003), ("K4_6_3_M9", 4, 6, 3, 9, 462)])
def test_registro_do_red_team_fecha_todos_os_perfis_da_dependencia_de_base(nome, q, n, R, M, perfis):
    """K_4(5,2) >= 12 (3003 perfis) sustenta s_min = 1 em K_4(6,3), M = 11; K_4(6,3) >= 10 (462 perfis), em K_4(7,4)."""
    import subprocess
    r = subprocess.run([sys.executable, str(FIB / "fecha_perfis.py"), "--q", str(q), "--n", str(n), "--R", str(R),
                        "--M", str(M), str(RT / "resultados" / f"{nome}.jsonl.xz")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"{perfis} perfis, {perfis} fechados" in r.stdout
