#!/bin/sh
# Compila o alvo CoveringHeavy com no máximo 2 módulos pesados ao mesmo tempo.
# Por quê: `lake build CoveringHeavy` solta até 4 processos Lean de ~9 GB; em 15 GB de RAM o OOM
# (exit 137) mata a compilação no meio (medido em 2026-10-03). Retomável: o lake pula o que já está pronto.
# Uso (da raiz do repo): sh tools/heavy_build_limitado.sh [paralelismo]
set -u
P="${1:-2}"
export PATH="$HOME/.elan/bin:$PATH"
cd "$(dirname "$0")/.."
lake build CoveringLean || exit 1
mods=$(ls CoveringLean | sed -n -e 's/^\(K[0-9]*_K[0-9]*_[0-9]*_[0-9]*_P[0-9]*\)\.lean$/\1/p' -e 's/^\(G610_Chunk_[0-9]*\)\.lean$/\1/p')
# a primeira folha de cada família compila sozinha, para os módulos compartilhados não serem construídos em duplicata
fam() { echo "$mods" | sed -e 's/_P[0-9]*$//' -e 's/_Chunk_[0-9]*$//' | sort -u; }
for f in $(fam); do
  first=$(echo "$mods" | grep "^${f}\(_P\|_Chunk_\)" | sort -V | head -1)
  echo "primeira folha de $f: $first"; lake build "CoveringLean.$first" || exit 1
done
echo "$mods" | sort -V | xargs -P "$P" -I{} sh -c 'lake build CoveringLean.{} >/dev/null 2>&1 && echo "ok {}" || echo "FALHOU {}"'
lake build CoveringHeavy
