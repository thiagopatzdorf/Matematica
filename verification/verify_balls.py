#!/usr/bin/env python3
"""verify_balls.py -- verificador B: união explícita das bolas de Hamming (NumPy).

Gera, por itertools, TODOS os vetores de erro e em (Z/7)^9 com wt(e) <= 4 (182 791) e marca, para cada
palavra c, os pontos (c + e) mod 7 num array de 7^9 posições. Não calcula distância entre pares:
a distância de x é o menor peso r tal que x caiu numa bola de raio r.

Também conta quantas palavras cobrem cada ponto (multiplicidade, raio 4), o que dá:
  duplicate_cover_hits = soma(mult) - pontos cobertos;
  palavras individualmente redundantes = c tal que todo ponto da sua bola tem mult >= 2.

Uso: verify_balls.py code.txt [N_esperado=1137]
"""
import hashlib, itertools, sys, time
import numpy as np

Q, N, R = 7, 9, 4
SPACE = Q ** N
POW = np.array([Q ** j for j in range(N)], dtype=np.int64)


def parse(path):
    raw = open(path, "rb").read()
    words = []
    for k, line in enumerate(raw.split(b"\n")[:-1], 1):
        if len(line) != N or any(ch < 48 or ch > 54 for ch in line):
            sys.exit(f"FAIL formato: linha {k} inválida")
        words.append([ch - 48 for ch in line])
    if not raw.endswith(b"\n"):
        sys.exit("FAIL formato: falta newline final")
    if len({tuple(w) for w in words}) != len(words):
        sys.exit("FAIL formato: palavras repetidas")
    return np.array(words, dtype=np.int64), hashlib.sha256(raw).hexdigest()


def errors_of_weight(w):
    out = []
    for pos in itertools.combinations(range(N), w):
        for vals in itertools.product(range(1, Q), repeat=w):
            e = [0] * N
            for p, v in zip(pos, vals):
                e[p] = v
            out.append(e)
    return np.array(out, dtype=np.int64).reshape(-1, N)


def main():
    path = sys.argv[1]
    esperado = int(sys.argv[2]) if len(sys.argv) > 2 else 1137
    t0 = time.time()
    C, sha = parse(path)
    E = [errors_of_weight(w) for w in range(R + 1)]
    sizes = [len(e) for e in E]
    assert sizes == [1, 54, 1296, 18144, 163296], sizes
    dist = np.full(SPACE, 255, dtype=np.uint8)
    for r in range(R + 1):                          # camadas: casca de raio r de cada palavra
        for c in C:
            idx = ((c + E[r]) % Q) @ POW
            sel = idx[dist[idx] == 255]
            dist[sel] = r
    Eall = np.concatenate(E)                        # bola de raio 4 inteira
    mult = np.zeros(SPACE, dtype=np.int64)
    balls = []
    for k in range(0, len(C), 64):
        chunk = [(((c + Eall) % Q) @ POW).astype(np.int32) for c in C[k:k + 64]]
        balls.extend(chunk)
        mult += np.bincount(np.concatenate(chunk), minlength=SPACE)
    redundant = [i for i, b in enumerate(balls) if mult[b].min() >= 2]
    unique_pts = [int((mult[b] == 1).sum()) for b in balls]
    hist = np.bincount(dist, minlength=256)
    Ncnt = {r: int(hist[r]) for r in range(R + 1)}
    uncovered = int(hist[255])
    covered = SPACE - uncovered
    maxd = max(r for r in range(R + 1) if Ncnt[r]) if uncovered == 0 else None
    far = np.flatnonzero(dist == maxd)[:3] if maxd is not None else []
    def word(i):
        return "".join(str((int(i) // Q ** j) % Q) for j in range(N))
    print("verificador B (união de bolas, Python/NumPy)")
    print(f"sha256 = {sha}")
    print(f"q = {Q}\nn = {N}\nR = {R}\n|C| = {len(C)}")
    for r in range(R + 1):
        print(f"N_{r} = {Ncnt[r]}")
    print(f"total = {sum(Ncnt.values()) + uncovered} (esperado {SPACE})")
    print(f"covered_count = {covered}\nmissing_count = {uncovered}")
    print(f"ball_hits = {int(mult.sum())} (= |C| * 182791 = {len(C) * 182791})")
    print(f"duplicate_cover_hits = {int(mult.sum()) - int((mult > 0).sum())}")
    print(f"max_multiplicity = {int(mult.max())}")
    print(f"max_distance = {maxd}\nfarthest_points = {Ncnt[maxd] if maxd is not None else 'n/a'}")
    for f in far:
        print(f"example_farthest = {word(f)}")
    print(f"min_unique_points_per_word = {min(unique_pts)} (palavra {word(C[int(np.argmin(unique_pts))] @ POW)})")
    print(f"total_exclusive_points = {sum(unique_pts)} (pontos cobertos por uma única palavra)")
    print(f"redundant_words = {len(redundant)}")
    for i in redundant[:20]:
        print(f"  redundante: {word(C[i] @ POW)}")
    ok = (len(C) == esperado and uncovered == 0 and maxd is not None and maxd <= R
          and int((mult > 0).sum()) == covered)
    print(f"runtime_internal_s = {time.time() - t0:.1f}")
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
