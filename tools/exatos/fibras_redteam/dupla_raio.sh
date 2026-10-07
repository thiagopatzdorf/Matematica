#!/bin/bash
# Dupla checagem de uma rodada de fibras com R < n - 2 (K_4(7,4) M = 9, K_3(7,3) M = 11), por dois caminhos que
# não dividem nada com a prova principal além do enunciado:
#  1. outro SOLVER: kissat (sem prova) em todas as instâncias da mesma CNF do fib_encode, os difíceis em cubos;
#  2. outra CODIFICAÇÃO: indep_raio.py (cobertura direta pela distância, sem projeções, quebra mínima) numa
#     amostra de perfis, com kissat.
# Uso: Q=4 N=7 R=4 M=9 [K=] [ORDEM=min] [AMOSTRA=40] [INST_CUBOS=246,372] KISSAT=... bash dupla_raio.sh SAIDA
set -eu
SAIDA=$1; mkdir -p "$SAIDA"
: "${Q:?}" "${N:?}" "${R:?}" "${M:?}" "${KISSAT:?}"
ORDEM=${ORDEM:-min}; AMOSTRA=${AMOSTRA:-40}; J=${J:-$(nproc)}; TEMPO=${TEMPO:-900}
KARG=(); [ -n "${K:-}" ] && KARG=(--k "$K")
AQUI=$(cd "$(dirname "$0")" && pwd); RAIZ=$(cd "$AQUI/../../.." && pwd)
export KISSAT
python3 "$RAIZ/tools/exatos/fibras/rodar.py" --q "$Q" --n "$N" --R "$R" --M "$M" --ordem "$ORDEM" "${KARG[@]}" \
  --solver kissat --tempo "$TEMPO" -j "$J" --dir "$SAIDA/kissat" ${INST_CUBOS:+--excluir "$INST_CUBOS"} | tail -n 3
if [ -n "${INST_CUBOS:-}" ]; then
  python3 "$RAIZ/tools/exatos/fibras/rodar.py" --q "$Q" --n "$N" --R "$R" --M "$M" --ordem "$ORDEM" "${KARG[@]}" \
    --solver kissat --tempo 20000 -j "$J" --dir "$SAIDA/kissat" --inst "$INST_CUBOS" --cubos 9 | tail -n 3
fi
# 2. amostra da codificação independente (perfis inteiros, k = n), sorteio fixo
python3 -c "
import random, sys
sys.path.insert(0, '$RAIZ/tools/exatos/fibras')
import fib_encode as e
q, n, R, M, a = $Q, $N, $R, $M, $AMOSTRA
_, ins = e.instancias(q, n, M, n, R=R)
rng = random.Random(2026)
for i in sorted(rng.sample(range(len(ins)), min(a, len(ins)))):
    print(i, ','.join(''.join(map(str, t)) for t in ins[i]))
" > "$SAIDA/amostra_indep.txt"
mkdir -p "$SAIDA/indep"
xargs -P "$J" -L 1 bash -c 'python3 '"$AQUI"'/indep_raio.py --q '"$Q"' --n '"$N"' --R '"$R"' --M '"$M"' --tipos "$1" --saida '"$SAIDA"'/indep/i$0.cnf; s=$(date +%s); timeout '"$TEMPO"' "$KISSAT" -q '"$SAIDA"'/indep/i$0.cnf > /dev/null; rc=$?; echo "$0 $1 rc=$rc $(( $(date +%s) - s ))s"; rm -f '"$SAIDA"'/indep/i$0.cnf' \
  < "$SAIDA/amostra_indep.txt" | tee "$SAIDA/indep.txt"
echo "indep: $(grep -c 'rc=20' "$SAIDA/indep.txt") UNSAT de $(wc -l < "$SAIDA/amostra_indep.txt"); SAT: $(grep -c 'rc=10' "$SAIDA/indep.txt")"
