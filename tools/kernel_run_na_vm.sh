#!/usr/bin/env bash
# Roda NA VM (ou qualquer máquina limpa) uma execução de kernel rastreável: clona o commit fixado, compila um alvo Lean com log bruto e
# gera o pacote de proveniência com a ferramenta (não à mão). Depois, o log e o prov.json são levados ao registro (`kernel-run register`).
#
#   tools/kernel_run_na_vm.sh <COMMIT> <ALVO> [SAIDA]
#   ex.: tools/kernel_run_na_vm.sh 1a5fa268dc916fde689e6aa801e591ac3c863b36 CoveringLean.Syn_K1887
#
# Variáveis: REPO_URL (padrão: o remote origin do checkout que contém este script), FACTORY_SRC (pasta src com factory_cauteloso/;
# obrigatória para gerar a proveniência), WORKDIR (padrão: $HOME/kernel-run-work), SAIDA (padrão: $WORKDIR/saida).
# Saída: build.log (log bruto, sem filtro), prov.json, tempos.txt (início/fim UTC da janela: inclui instalação do elan e `lake exe cache get`).
set -euo pipefail

COMMIT="${1:?uso: $0 <COMMIT> <ALVO> [SAIDA]}"
ALVO="${2:?uso: $0 <COMMIT> <ALVO> [SAIDA]}"
WORKDIR="${WORKDIR:-$HOME/kernel-run-work}"
SAIDA="${3:-${SAIDA:-$WORKDIR/saida}}"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="${REPO_URL:-$(git -C "$AQUI" remote get-url origin)}"
: "${FACTORY_SRC:?defina FACTORY_SRC (pasta src que contém factory_cauteloso/)}"

case "$COMMIT" in
  *[!0-9a-f]*|"") echo "erro: COMMIT deve ser o sha completo (40 hex), não um nome de branch" >&2; exit 2 ;;
esac
[ "${#COMMIT}" -eq 40 ] || { echo "erro: COMMIT deve ter 40 hex" >&2; exit 2; }

mkdir -p "$SAIDA"
date -u +%Y-%m-%dT%H:%M:%SZ > "$SAIDA/inicio.txt"

if ! command -v lake >/dev/null 2>&1; then
  export PATH="$HOME/.elan/bin:$PATH"
fi
if ! command -v lake >/dev/null 2>&1; then
  curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
fi

rm -rf "$WORKDIR/repo"
git clone --quiet "$REPO_URL" "$WORKDIR/repo"
cd "$WORKDIR/repo"
git checkout --quiet --detach "$COMMIT"
[ "$(git rev-parse HEAD)" = "$COMMIT" ] || { echo "erro: HEAD != COMMIT" >&2; exit 3; }

# o cache do Mathlib é só aceleração; falhar aqui não invalida nada (o build compilaria do zero)
lake exe cache get || echo "aviso: lake exe cache get falhou; o build vai compilar o Mathlib" >&2

# log bruto SEM filtro: é ele que vira evidência (sha256, #print axioms, contagens medidas dele)
set +e
lake build "$ALVO" > "$SAIDA/build.log" 2>&1
RC=$?
set -e
date -u +%Y-%m-%dT%H:%M:%SZ > "$SAIDA/fim.txt"
{ echo "inicio $(cat "$SAIDA/inicio.txt")"; echo "fim $(cat "$SAIDA/fim.txt")"; echo "rc_lake_build $RC"; } > "$SAIDA/tempos.txt"

# proveniência gerada pela ferramenta NESTA máquina (host via metadata do GCE, toolchain via lean/lake/git), não escrita à mão
PYTHONPATH="$FACTORY_SRC" python3 -m factory_cauteloso.matematica.kernel --raiz-fontes "$WORKDIR/repo" --saida "$SAIDA/prov.json" provenance

echo "pronto: $SAIDA (build.log, prov.json, tempos.txt); rc do build = $RC"
exit "$RC"
