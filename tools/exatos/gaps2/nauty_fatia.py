#!/usr/bin/env python3
"""Lista da fatia mínima com canonização por nauty (aumento canônico de McKay).

`aumento.py` guarda o grupo S_q wr S_m inteiro numa tabela e só vai até m <= 4 com q = 3.
Aqui a forma canônica vem do nauty (`libnauty`, `nauty_fatia.c`), e o grupo nunca é listado:
serve para Z_3^5 (|G| = 933 120) e Z_3^6 (|G| = 33 592 320).

Codificação (prova de que forma canônica igual <=> mesma órbita). Para um conjunto X de pontos
distintos de Z_q^m, o grafo colorido Γ(X) tem: m vértices de coordenada (cor 0), q·m vértices de
símbolo (i,a) (cor 1), um vértice por ponto de X (cor 2); arestas i—(i,a) e x—(i, x_i).
 (⇒) Se Y = g(X) com g = (σ; π_0..π_{m−1}) ∈ S_q wr S_m (coordenada i vai para σ(i), símbolo a
     da coordenada i vai para π_i(a)), o mapa i ↦ σ(i), (i,a) ↦ (σ(i), π_i(a)), x ↦ g(x)
     preserva cores e arestas: Γ(X) ≅ Γ(Y).
 (⇐) Seja φ: Γ(X) → Γ(Y) um isomorfismo que preserva cores. Ele leva coordenadas em coordenadas
     (σ) e, como (i,a) só é vizinho da coordenada i entre os vértices de cor 0, leva os símbolos
     de i nos símbolos de σ(i) (π_i). Isso define g ∈ S_q wr S_m. Um ponto x é vizinho
     exatamente de (i, x_i), i = 0..m−1, então φ(x) é o ponto de Y vizinho de (σ(i), π_i(x_i))
     para todo i, isto é, φ(x) = g(x) (os pontos de Y são distintos, então há um só). Logo
     g(X) = Y.
O rótulo canônico do nauty para grafos com partição ordenada de cores dá grafos canônicos
iguais se e só se existe isomorfismo que preserva as cores (em ordem). Então forma canônica
igual <=> mesma órbita.

Filtro. ov(X) = |X|·V(m,R) − |cob(X)|; |U(X)| <= cap equivale a ov(X) <= orc com
orc = s·V(m,R) − q^m + cap. ov só cresce com X (tirar um ponto x diminui ov de
|B(x) ∩ cob(X − x)| >= 0), então todo subconjunto de um conjunto válido é válido.

Completude do aumento (McKay 1998, "Isomorph-free exhaustive generation"). Deleção canônica
m(Y): entre os pontos de Y com maior sobreposição marginal mo_Y(y) = |B(y) ∩ cob(Y − y)|, o de
maior rótulo canônico. mo é invariante por isometria e o rótulo canônico é equivariante, então
m(g(Y)) está na órbita de Aut(g(Y)) de g(m(Y)). O filho X+p de um nó X é aceito se p está na
órbita de Aut(X+p) de m(X+p), e só um filho por classe entre os filhos do mesmo pai (comparando
os grafos canônicos). Indução em k: (a) toda órbita de k-conjuntos válidos aparece: se Y é
válido, Y − m(Y) é válido, tem um representante X na árvore por hipótese, e a isometria h com
h(Y − m(Y)) = X leva Y em X + h(m(Y)), que é aceito (h(m(Y)) está na órbita de m(X + h(m(Y))));
o descarte por repetição só tira filhos isomorfos a outro já aceito do mesmo pai. (b) nenhuma
aparece duas vezes: se X+p (pai X) e X'+p' (pai X') são isomorfos e ambos aceitos, então
X = (X+p) − p ≅ (X+p) − m(X+p) ≅ (X'+p') − m(X'+p') ≅ X', logo X = X' pela hipótese, e o
descarte por repetição deixa um só.

Poda (não muda a lista, só corta nós sem descendente válido). Num caminho da árvore,
mo_{X_{i+1}}(p_{i+1}) >= mo_{X_{i+1}}(p_i) >= mo_{X_i}(p_i), porque p_{i+1} é máximo em X_{i+1}
e cobertura só cresce. Como ov(X_s) = ov(X_k) + Σ_{i>k} mo_{X_i}(p_i) e
mo_{X_i}(p_i) >= |B(p_i) ∩ cob(X_k)|, vale ov(X_s) >= ov(X_k) + (soma dos s−k menores
max(mo_k, δ(p))), δ(p) = |B(p) ∩ cob(X_k)|. Nó que viola isso não tem descendente com ov <= orc.

  python3 tools/exatos/gaps2/nauty_fatia.py --q 3 --n 5 --R 1 --M 26 --listar inst.json -j 4
  python3 tools/exatos/gaps2/nauty_fatia.py --q 3 --n 6 --R 1 --M 72 --s 18 --contar -j 4
  python3 tools/exatos/gaps2/nauty_fatia.py --q 3 --n 7 --R 2 --M 27 --s 7 --estimar 2000
"""
import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fatia  # noqa: E402

FONTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nauty_fatia.c")


def binario():
    """Compila nauty_fatia.c (uma vez por versão da fonte) e devolve o caminho do executável."""
    if os.environ.get("NAUTY_FATIA_BIN"):
        return os.environ["NAUTY_FATIA_BIN"]
    h = hashlib.sha256(open(FONTE, "rb").read()).hexdigest()[:12]
    exe = os.path.join(tempfile.gettempdir(), f"nauty_fatia-{h}")
    if not os.path.exists(exe):
        tmp = exe + f".{os.getpid()}"
        subprocess.run(["gcc", "-O3", "-DWORDSIZE=64", "-DMAXN=WORDSIZE", FONTE, "-lnautyL1", "-lm",
                        "-o", tmp], check=True)
        os.replace(tmp, exe)
    return exe


def orcamento(q, m, s, R, cap):
    return s * fatia.vol(m, R, q) - q ** m + cap


def _rodar(args):
    r = subprocess.run([binario()] + [str(a) for a in args], capture_output=True, text=True, check=True)
    return r.stdout


def _partes(modo, q, m, s, R, cap, j, corte, partes=None):
    """Roda a árvore inteira (j = 1) ou em `partes` pedaços (nós do nível `corte` repartidos por
    índice módulo `partes`) num pool de j processos; mais pedaços que processos equilibra a carga."""
    orc = orcamento(q, m, s, R, cap)
    if j <= 1:
        return [_rodar([modo, q, m, R, s, orc])]
    W = partes or 16 * j
    with ThreadPoolExecutor(j) as ex:
        return list(ex.map(_rodar, [[modo, q, m, R, s, orc, W, w, min(corte, s)] for w in range(W)]))


def contar(q, m, s, R, cap, j=1, corte=4, partes=None):
    """(número de órbitas válidas, nós por nível, chamadas ao nauty)."""
    if orcamento(q, m, s, R, cap) < 0:
        return 0, [0] * (s + 1), 0
    niveis, cham = [0] * (s + 1), 0
    W = (partes or 16 * j) if j > 1 else 1
    for out in _partes("conta", q, m, s, R, cap, j, corte, W):
        for ln in out.splitlines():
            t = ln.split()
            if t[0] == "nivel":
                niveis[int(t[1])] += int(t[2])
            elif t[0] == "chamadas":
                cham += int(t[1])
    if W > 1:  # os níveis acima do corte são refeitos por todo pedaço
        for k in range(min(corte, s)):
            niveis[k] //= W
    return niveis[s], niveis, cham


def amostrar_partes(q, m, s, R, cap, partes, corte, k, semente=1, j=1):
    """Estimativa medida (não chute) do total: sorteia k das `partes` partes da árvore (nós do
    nível `corte` repartidos por índice módulo `partes`), conta cada parte sorteada por inteiro e
    devolve total ≈ partes·média, com erro padrão partes·dp/√k (amostragem sem reposição, sem a
    correção de população finita, que só diminuiria o erro). Também extrapola os segundos."""
    import random
    import statistics
    orc = orcamento(q, m, s, R, cap)
    ws = random.Random(semente).sample(range(partes), k)

    def uma(w):
        t0 = time.time()
        out = _rodar(["conta", q, m, R, s, orc, partes, w, corte])
        seg = time.time() - t0
        folhas = [int(ln.split()[2]) for ln in out.splitlines() if ln.startswith(f"nivel {s} ")][0]
        return folhas, seg

    with ThreadPoolExecutor(j) as ex:
        res = list(ex.map(uma, ws))
    f = [r[0] for r in res]
    t = [r[1] for r in res]
    dp = statistics.stdev(f) if k > 1 else 0.0
    dpt = statistics.stdev(t) if k > 1 else 0.0
    return {"partes": partes, "corte": corte, "sorteadas": ws, "folhas_por_parte": f,
            "segundos_por_parte": [round(x, 2) for x in t],
            "orbitas_estimadas": partes * statistics.mean(f), "erro_padrao": partes * dp / k ** 0.5,
            "segundos_cpu_estimados": partes * statistics.mean(t), "erro_padrao_seg": partes * dpt / k ** 0.5}


def contar_parcial(q, m, s, R, cap, partes, corte, prazo, j=1, log=None):
    """Conta partes inteiras (em ordem aleatória fixa) até o prazo em segundos de parede. Devolve
    cotas INFERIORES medidas: órbitas nas partes concluídas e segundos de CPU gastos (as partes
    interrompidas também gastaram CPU, que entra só como parede). Serve para decidir "não cabe"
    sem depender de estimador: em K_3(6,1) s* = 19 o estimador por partes sorteadas errou por 100x
    (cauda pesada), ver docs/exatos/FATIA_NAUTY.md."""
    import random
    orc = orcamento(q, m, s, R, cap)
    ordem = list(range(partes))
    random.Random(1).shuffle(ordem)
    fim = time.time() + prazo
    feitas, folhas, cpu = 0, 0, 0.0
    procs = {}
    fila = iter(ordem)
    exe = binario()

    def lanca():
        w = next(fila, None)
        if w is None:
            return False
        p = subprocess.Popen([exe, "conta", str(q), str(m), str(R), str(s), str(orc), str(partes), str(w),
                              str(corte)], stdout=subprocess.PIPE, text=True)
        procs[p] = (w, time.time())
        return True

    for _ in range(j):
        lanca()
    while procs and time.time() < fim:
        for p in list(procs):
            if p.poll() is None:
                continue
            w, t0 = procs.pop(p)
            out = p.stdout.read()
            f = [int(ln.split()[2]) for ln in out.splitlines() if ln.startswith(f"nivel {s} ")][0]
            feitas += 1
            folhas += f
            cpu += time.time() - t0
            if log:
                log.write(json.dumps({"parte": w, "folhas": f, "seg": round(time.time() - t0, 2)}) + "\n")
                log.flush()
            lanca()
        time.sleep(0.2)
    for p in procs:
        p.kill()
    return {"partes": partes, "corte": corte, "concluidas": feitas, "orbitas_nas_concluidas": folhas,
            "seg_cpu_nas_concluidas": round(cpu, 1), "interrompidas": len(procs), "prazo_s": prazo}


def configuracoes(q, m, s, R, cap, j=1, corte=4):
    """Um representante (lista de pontos) por órbita de s-conjuntos de Z_q^m com |U| <= cap."""
    if s == 0:
        return [[]] if q ** m <= cap else []
    if orcamento(q, m, s, R, cap) < 0:
        return []
    P = list(itertools.product(range(q), repeat=m))
    out = []
    for txt in _partes("lista", q, m, s, R, cap, j, corte):
        for ln in txt.splitlines():
            if ln.startswith("X "):
                out.append(sorted(P[int(v)] for v in ln.split()[1:]))
    return sorted(out)


def estimar(q, m, s, R, cap, sondas, semente=1):
    """Estimador de Knuth da árvore: (nós por nível com erro padrão, chamadas estimadas, segundos)."""
    orc = orcamento(q, m, s, R, cap)
    if orc < 0:
        return {"niveis": [[0, 0]] * (s + 1), "chamadas": [0, 0], "segundos": 0.0, "feitas": 0}
    t0 = time.time()
    out = _rodar(["estima", q, m, R, s, orc, sondas, semente])
    seg = time.time() - t0
    niveis, cham, feitas = [], None, 0
    for ln in out.splitlines():
        t = ln.split()
        if t[0] == "nivel":
            niveis.append([float(t[2]), float(t[3])])
        elif t[0] == "chamadas_estimadas":
            cham = [float(t[1]), float(t[2])]
        elif t[0] == "chamadas":
            feitas = int(t[1])
    return {"niveis": niveis, "chamadas": cham, "segundos": seg, "feitas": feitas}


def forma(q, m, pontos):
    """Forma canônica (texto hex do grafo canônico) de um conjunto de pontos de Z_q^m."""
    P = {p: i for i, p in enumerate(itertools.product(range(q), repeat=m))}
    ent = f"{len(pontos)} " + " ".join(str(P[tuple(p)]) for p in pontos) + "\n"
    r = subprocess.run([binario(), "canon", str(q), str(m)], input=ent, capture_output=True, text=True,
                       check=True)
    return r.stdout.strip()


def instancias(q, n, R, M, j=1, so_s=None):
    out = []
    for s in range(0, M // q + 1):
        if so_s is not None and s not in so_s:
            continue
        cap = (M - s) * fatia.vol(n - 1, R - 1, q)
        for K in configuracoes(q, n - 1, s, R, cap, j):
            for t in fatia.blocos_restantes(q, M, s):
                out.append((s, tuple(tuple(k) for k in K), t))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--s", type=int, action="append", help="só estes s* (repetível)")
    ap.add_argument("--listar")
    ap.add_argument("--contar", action="store_true")
    ap.add_argument("--estimar", type=int, metavar="SONDAS")
    ap.add_argument("--semente", type=int, default=1)
    ap.add_argument("--parcial", nargs=3, type=int, metavar=("PARTES", "CORTE", "PRAZO_S"),
                    help="conta partes inteiras até o prazo; devolve cotas inferiores medidas")
    ap.add_argument("--amostrar", nargs=3, type=int, metavar=("PARTES", "CORTE", "K"),
                    help="conta k partes sorteadas de PARTES (nível CORTE) e extrapola")
    ap.add_argument("-j", type=int, default=1)
    a = ap.parse_args()
    m = a.n - 1
    ss = a.s if a.s else list(range(0, a.M // a.q + 1))
    if a.listar:
        ins = instancias(a.q, a.n, a.R, a.M, a.j, set(ss))
        json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(a.listar, "w"))
        print(f"{len(ins)} instâncias -> {a.listar}")
        return
    for s in ss:
        cap = (a.M - s) * fatia.vol(m, a.R - 1, a.q)
        info = {"q": a.q, "n": a.n, "R": a.R, "M": a.M, "s": s, "cap": cap,
                "orc": orcamento(a.q, m, s, a.R, cap)}
        t0 = time.time()
        if a.contar:
            c, niv, ch = contar(a.q, m, s, a.R, cap, a.j)
            info.update(orbitas=c, niveis=niv, chamadas=ch, segundos=round(time.time() - t0, 2))
        elif a.parcial:
            info.update(contar_parcial(a.q, m, s, a.R, cap, *a.parcial, a.j))
        elif a.amostrar:
            info.update(amostrar_partes(a.q, m, s, a.R, cap, *a.amostrar, a.semente, a.j))
        elif a.estimar:
            info.update(estimar(a.q, m, s, a.R, cap, a.estimar, a.semente))
        print(json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
