#!/bin/bash
# K_4(6,3), M = 11: os 8008 perfis do lema das fibras (s_min = 1: K_4(5,2) = 16 > 11 exclui fibra vazia), cobertura
# por triplas (R = n - 3). Todos UNSAT com LRAT conferido => K_4(6,3) >= 12 (antes 11, HSPQ; cota superior 14).
set -eu
export Q=4 N=6 R=3 M=11 ORDEM=${ORDEM:-max}
exec bash pesado/jobs/_fibras_comum.sh
