#!/usr/bin/env bash
# Confere todos os códigos do repositório com o verificador oficial (tools/verify/verify.c).
#
#   tools/verify/check_all.sh            # da raiz do repo; compila o verificador se preciso
#
# Para cada data/codes/q<Q>_n<N>_R<R>_M<M>.txt:
#   1. verify no .txt: dígitos < q, comprimento n, sem duplicata, |C| = M e 0 pontos descobertos;
#   2. se existe data/structured/<mesmo nome>.json: expand.py (que confere o canonical_sha256
#      declarado) | verify, e o sha256 canônico das duas leituras tem de ser o mesmo.
# E todo JSON de data/structured precisa ter o .txt correspondente (nada órfão).
# Sai com 1 no primeiro defeito, depois de imprimir a linha dele.
set -euo pipefail
cd "$(dirname "$0")/../.."

BIN="${VERIFY_BIN:-tools/verify/verify}"
if [[ ! -x "$BIN" || tools/verify/verify.c -nt "$BIN" ]]; then
  "${CC:-cc}" -O2 -std=c99 -Wall -Wextra -Werror -o "$BIN" tools/verify/verify.c
fi

sha_of() { sed -n 's/.* sha256=\([0-9a-f]\{64\}\).*/\1/p'; }
fail=0
n=0
for txt in data/codes/*.txt; do
  name=$(basename "$txt" .txt)
  out=$("$BIN" "$txt") || { echo "FALHA $txt: $out"; exit 1; }
  echo "ok   $txt  $out"
  s_txt=$(sha_of <<<"$out")
  json="data/structured/$name.json"
  if [[ -f "$json" ]]; then
    IFS=_ read -r q nn r m <<<"$name"
    out2=$(python3 scripts/codes/expand.py "$json" 2>/dev/null \
           | "$BIN" -q "${q#q}" -n "${nn#n}" -r "${r#R}" -m "${m#M}" -) || { echo "FALHA $json: $out2"; exit 1; }
    s_json=$(sha_of <<<"$out2")
    if [[ "$s_json" != "$s_txt" ]]; then
      echo "FALHA $json: sha256 canônico $s_json != $s_txt do .txt"; exit 1
    fi
    echo "ok   $json  (expand -> mesmo sha256 canônico)"
  fi
  n=$((n + 1))
done
for json in data/structured/*.json; do
  [[ -f "data/codes/$(basename "$json" .json).txt" ]] || { echo "FALHA $json sem .txt em data/codes"; fail=1; }
done
[[ $fail == 0 ]] || exit 1
echo "check_all: $n códigos, todos cobrem (0 pontos descobertos)."
