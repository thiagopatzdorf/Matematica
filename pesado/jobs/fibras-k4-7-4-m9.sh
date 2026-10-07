#!/bin/bash
# K_4(7,4), M = 9: os 792 perfis do lema das fibras (s_min = 1), cobertura por triplas (R = n - 3).
# Todos UNSAT com LRAT conferido => não existe código com 9 palavras => K_4(7,4) = 10 (a cota superior 10
# é de Rivas Soriano). Shard i roda os perfis de índice = i (mod SHARD_TOTAL). Saída: JSONL por perfil.
# Medido na factory-01 (carregada): perfis de 26 s a alguns minutos sem prova.
set -eu
export Q=4 N=7 R=4 M=9
exec bash pesado/jobs/_fibras_comum.sh
