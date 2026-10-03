#!/usr/bin/env python3
"""measure.py -- roda um comando e imprime runtime (relógio) e pico de memória (RSS máx. do filho).
Uso: measure.py <cmd> [args...]   (sai com o código do comando)"""
import resource, subprocess, sys, time
t = time.time()
rc = subprocess.call(sys.argv[1:])
dt = time.time() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"runtime_s = {dt:.2f}\ncpu_s = {ru.ru_utime + ru.ru_stime:.2f}\npeak_memory_kb = {ru.ru_maxrss}\nexit_code = {rc}", flush=True)
sys.exit(rc)
