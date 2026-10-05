"""Instância (s, K) de "K_q(n,R) <= M" como restrições 0-1, em OPB (RoundingSat + VeriPB) ou CNF
(CaDiCaL + LRAT conferido pelo lrat-check). A prova de validade das restrições está em
docs/exatos/k362/K3_M15_REPRODUCAO.md, seção 2.

Relaxação projetada ("fatia"): variáveis w_y, y em Z_q^(n-1), com w_y = [existe b != 0, (b,y) em C].
  tamanho:   sum_y w_y <= M - s
  cobertura: para todo y a distância > R de K, sum_{d(y,y') <= R-1} w_y' >= 1
Formulação completa (só se a relaxação for satisfazível): z_c para c em Z_q^n com c_0 != 0, a fatia
c_0 = 0 fixa em {0} x K, cobertura de raio R de todo ponto, sum z_c <= M - s e as fibras
sum_{c_j = a} z_c >= s - #{k em K : k_j = a} para j >= 1 (s é a menor fibra).
"""
import hashlib
import itertools
import os
import resource
import signal
import subprocess
import tempfile
import time

import numpy as np


def _dist(A, B):
    return (A[:, None, :] != B[None, :, :]).sum(axis=2)


def restricoes(q, n, R, M, K, completa=False):
    """(cobertura, nv, teto, fibras): cláusulas "algum literal", sum x <= teto e, na completa,
    pares (literais, k) com sum >= k (fibras da coordenada j >= 1, pois s é a menor fibra)."""
    s = len(K)
    if not completa:
        P = np.array(list(itertools.product(range(q), repeat=n - 1)))
        dK = _dist(np.array(K).reshape(-1, n - 1), P).min(axis=0) if s else np.full(len(P), n)
        D = _dist(P, P)
        cob = [[int(j) + 1 for j in np.nonzero(D[y] <= R - 1)[0]] for y in range(len(P)) if dK[y] > R]
        return cob, len(P), M - s, []
    P = np.array(list(itertools.product(range(q), repeat=n)))
    livres = P[P[:, 0] != 0]
    fixos = np.array([[0] + list(k) for k in K]).reshape(-1, n)
    dF = _dist(fixos, P).min(axis=0) if s else np.full(len(P), n + 1)
    D = _dist(P, livres)
    cob = [[int(j) + 1 for j in np.nonzero(D[x] <= R)[0]] for x in range(len(P)) if dF[x] > R]
    fib = [([int(i) + 1 for i in np.nonzero(livres[:, j] == a)[0]], s - int((fixos[:, j] == a).sum()))
           for j in range(1, n) for a in range(q)]
    return cob, len(livres), M - s, [f for f in fib if f[1] > 0]


def opb(cob, nv, teto, fib=()):
    L = [" ".join("+1 x%d" % v for v in c) + " >= 1 ;" for c in cob]
    L.append(" ".join("-1 x%d" % v for v in range(1, nv + 1)) + " >= %d ;" % -teto)
    L += [" ".join("+1 x%d" % v for v in lits) + " >= %d ;" % k for lits, k in fib]
    return "* #variable= %d #constraint= %d #equal= 0 intsize= 8\n" % (nv, len(L)) + "\n".join(L) + "\n"


def cnf(cob, nv, teto, fib=()):
    """Cobertura como cláusulas; cada "sum <= k" por um totalizador (Bailleux-Boufkhad) truncado em
    k + 1 saídas; "sum lits >= k" vira "sum (não lits) <= len - k"."""
    cls = [list(c) for c in cob]
    top = [nv]

    def novo():
        top[0] += 1
        return top[0]

    def tot(xs, k):
        """Saídas o_1..o_m (m <= k+1), o_j verdadeiro se ao menos j dos xs o forem."""
        if len(xs) == 1:
            return list(xs)
        a, b = tot(xs[:len(xs) // 2], k), tot(xs[len(xs) // 2:], k)
        o = [novo() for _ in range(min(len(a) + len(b), k + 1))]
        for i in range(len(a) + 1):
            for j in range(len(b) + 1):
                if 0 < i + j <= len(o):
                    cls.append(([-a[i - 1]] if i else []) + ([-b[j - 1]] if j else []) + [o[i + j - 1]])
        return o

    def no_maximo(xs, k):
        o = tot(xs, k)
        if len(o) > k:
            cls.append([-o[k]])
    no_maximo(list(range(1, nv + 1)), teto)
    for lits, k in fib:
        no_maximo([-v for v in lits], len(lits) - k)
    return "p cnf %d %d\n" % (top[0], len(cls)) + "".join(" ".join(map(str, c)) + " 0\n" for c in cls)


# Teto do arquivo de prova: uma prova VeriPB de M = 16 passou de 10 GB em 20 min e encheria o disco.
# Acima dele o solver morre por SIGXFSZ e a instância fica em aberto (veredito "PROVA_GRANDE").
MAX_PROVA = int(os.environ.get("K362_REPRO_MAX_PROVA_GB", "4")) << 30


GRANDE = (-signal.SIGXFSZ, 128 + signal.SIGXFSZ)


def _teto_arquivo():
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_PROVA, MAX_PROVA))


def _roda(cmd, tempo):
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=tempo, preexec_fn=_teto_arquivo)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess(cmd, -9, "", "")
    return r, round(time.time() - t, 3)


def resolver(texto, formato, binarios, nv, tempo=3600):
    """formato 'opb' (roundingsat, veripb) ou 'cnf' (cadical, lrat-check); modelo restrito a x_1..x_nv.
    Fórmula e prova vivem num diretório temporário: só o registro sai daqui."""
    out = {"formato": formato, "sha256": hashlib.sha256(texto.encode()).hexdigest()}
    with tempfile.TemporaryDirectory() as d:
        f, p = os.path.join(d, "f." + formato), os.path.join(d, "prova")
        open(f, "w").write(texto)
        if formato == "opb":
            r, out["t_solver"] = _roda([binarios["roundingsat"], f, "--print-sol=1", "--proof-log=" + p], tempo)
            st = [ln[2:].strip() for ln in r.stdout.splitlines() if ln.startswith("s ")]
            out["veredito"] = {"UNSATISFIABLE": "UNSAT", "SATISFIABLE": "SAT"}.get(st[-1] if st else "", "TEMPO")
            if r.returncode in GRANDE:
                out["veredito"] = "PROVA_GRANDE"
        else:
            r, out["t_solver"] = _roda([binarios["cadical"], "-q", "--lrat=true", "--binary=false", f, p], tempo)
            out["veredito"] = {20: "UNSAT", 10: "SAT"}.get(r.returncode, "PROVA_GRANDE" if r.returncode in GRANDE
                                                                   else "TEMPO")
        if out["veredito"] == "SAT":
            out["modelo"] = [int(x[1:] if x.startswith("x") else x) for ln in r.stdout.splitlines()
                             if ln.startswith("v ") for x in ln.split()[1:] if not x.startswith("-")]
            out["modelo"] = [x for x in out["modelo"] if 0 < x <= nv]
        if out["veredito"] != "UNSAT":
            return out
        out["prova_bytes"] = os.path.getsize(p)
        if formato == "opb":
            v, out["t_verif"] = _roda([binarios["veripb"], f, p], tempo)
            ok = v.returncode == 0 and "s VERIFIED UNSATISFIABLE" in v.stdout
        else:
            v, out["t_verif"] = _roda([binarios["lrat-check"], f, p], tempo)
            ok = v.returncode == 0 and "c VERIFIED" in v.stdout
        out["verificador"] = "VERIFIED" if ok else "FALHOU"
        return out


def codigo_do_modelo(q, n, K, modelo):
    """Palavras do código: {0} x K mais as livres (c_0 != 0) marcadas no modelo da formulação completa."""
    P = list(itertools.product(range(q), repeat=n))
    livres = [c for c in P if c[0] != 0]
    return [(0,) + tuple(k) for k in K] + [livres[v - 1] for v in modelo]


def raio(q, n, C):
    P = np.array(list(itertools.product(range(q), repeat=n)))
    return int(_dist(np.array(C), P).min(axis=0).max())
