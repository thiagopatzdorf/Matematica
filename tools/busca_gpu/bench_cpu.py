#!/usr/bin/env python3
"""Base de CPU do PoC de GPU: roda `tabu` (tools/busca_direta/tabu.c, compilado em $TABU_BIN) em P processos
paralelos, uma semente por processo, no MESMO alvo M, e mede o tempo até o 1º ACHOU (stdout "M arquivo") e as
iterações por segundo (linha "fim it=" do stderr). Uso: bench_cpu.py q n R M segundos processos semente0 [tenure]"""
import os, subprocess, sys, time, tempfile

q, n, R, M = (int(x) for x in sys.argv[1:5])
secs, procs, s0 = float(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
tenure = sys.argv[8] if len(sys.argv) > 8 else "1"
binario = os.environ.get("TABU_BIN", "tabu")
tmp = tempfile.mkdtemp()
t0 = time.time()
ps = []
for i in range(procs):
    p = subprocess.Popen([binario, str(q), str(n), str(R), str(M), str(secs), str(s0 + i), f"{tmp}/s{i}", tenure],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ps.append(p)
res = []
for i, p in enumerate(ps):
    out, err = p.communicate()
    # tempo até o 1º ACHOU: o arquivo <prefixo>_M<M>.txt do alvo, mtime - t0
    f = f"{tmp}/s{i}_M{M}.txt"
    t_ach = os.path.getmtime(f) - t0 if os.path.exists(f) else None
    it = None
    for ln in err.splitlines():
        if ln.startswith("fim it="):
            it = int(ln.split()[1].split("=")[1])
    res.append((i, t_ach, it))
tot_it = sum(r[2] or 0 for r in res)
ok = [r[1] for r in res if r[1] is not None]
print(f"CPU q={q} n={n} R={R} M={M} procs={procs} secs={secs}: sucessos={len(ok)}/{procs} "
      f"tempos={[round(x, 1) for x in sorted(ok)]} it_total={tot_it} it_por_s_total={tot_it / secs:.0f} "
      f"it_por_s_por_proc={tot_it / secs / procs:.0f}")
