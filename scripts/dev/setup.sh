#!/usr/bin/env bash
# Prepara o ambiente de desenvolvimento: venv em .venv + dependências. Idempotente:
# rodar de novo só confirma o que já está instalado.
set -euo pipefail
cd "$(dirname "$0")/../.."

PY="${PYTHON:-python3}"
[ -d .venv ] || "$PY" -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate

python -m pip install --quiet --upgrade pip
# Mesmas versões do CI (.github/workflows/ci.yml); subir de versão é decisão, não acidente.
python -m pip install --quiet pytest==8.4.2 numpy==2.4.6 ruff==0.15.20 httpx pre-commit \
  -r infinito/requirements.txt

# O pre-commit só é instalado dentro de um checkout git.
if [ -d .git ] || [ -f .git ]; then
  pre-commit install --install-hooks >/dev/null
fi

echo "ok: ambiente pronto. Use 'make ajuda' para ver os alvos."
