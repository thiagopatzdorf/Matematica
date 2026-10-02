#!/usr/bin/env python3
"""Valida o formato do witness: N linhas, cada uma com exatamente 9 caracteres em 0..6, sem repetição,
em ordem lexicográfica estrita, terminando em '\\n'. Imprime o sha256 e sai com 1 em qualquer falha.
Uso: validate_witness.py code_1137.txt [N_esperado=1137]"""
import hashlib, sys
path = sys.argv[1]; esperado = int(sys.argv[2]) if len(sys.argv) > 2 else 1137
raw = open(path, 'rb').read()
erros = []
if not raw.endswith(b'\n'): erros.append('arquivo não termina em \\n')
linhas = raw.decode('ascii', errors='replace').split('\n')[:-1]
for i, l in enumerate(linhas, 1):
    if len(l) != 9 or any(ch not in '0123456' for ch in l):
        erros.append(f'linha {i}: palavra inválida {l!r}')
if len(set(linhas)) != len(linhas): erros.append(f'{len(linhas) - len(set(linhas))} duplicatas')
if linhas != sorted(set(linhas)): erros.append('não está em ordem canônica (lexicográfica estrita)')
if len(linhas) != esperado: erros.append(f'{len(linhas)} palavras, esperado {esperado}')
print(f'palavras={len(linhas)} sha256={hashlib.sha256(raw).hexdigest()}')
if erros:
    print('FAIL'); [print('  ' + e) for e in erros[:20]]; sys.exit(1)
print('PASS formato: q=7 n=9 |C|=%d, 0 duplicatas, 0 inválidas' % len(linhas))
