#!/bin/bash
# K_3(7,3), M = 11: os 11 440 perfis do lema das fibras (s_min = 1), cobertura por 4-uplas (R = n - 4).
# Todos UNSAT com LRAT conferido => K_3(7,3) = 12 (cota superior 12 de Hämäläinen–Rankinen 1991).
set -eu
export Q=3 N=7 R=3 M=11
exec bash pesado/jobs/_fibras_comum.sh
