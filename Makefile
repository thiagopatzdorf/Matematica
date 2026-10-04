# Alvos de desenvolvimento. `make ajuda` lista todos. Usa o .venv se existir (scripts/dev/setup.sh).
SHELL := /bin/bash
VENV := $(wildcard .venv/bin)
PY := $(if $(VENV),.venv/bin/python,python3)
RUFF := $(PY) -m ruff

# Testes medidos em >5 s (de ~80 s no total): ficam fora do alvo rápido, entram em `make test` e no CI.
RAPIDO_FORA := --deselect tests/test_code_format.py::GeneratorsRegenerateTheCodes \
  --deselect tests/test_verify.py::VerifierTest

.DEFAULT_GOAL := ajuda
.PHONY: ajuda setup test test-rapido lint verifica-codigos lean-rapido higiene

ajuda: ## Lista os alvos
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-17s %s\n", $$1, $$2}'

setup: ## Cria o .venv e instala as dependências (idempotente)
	scripts/dev/setup.sh

test: ## Suíte completa: tests + infinito/tests
	$(PY) -m pytest -q tests infinito/tests

test-rapido: ## Suíte sem os 4 testes de >5 s (regerar JSON e verificador C), para o ciclo de edição
	$(PY) -m pytest -q -m "not lento and not lean" $(RAPIDO_FORA) tests infinito/tests

lint: ## ruff check (conjunto de regras do pyproject.toml)
	$(RUFF) check .

verifica-codigos: ## Compila o verificador C e confere todo data/codes
	cc -O2 -std=c99 -Wall -Wextra -Werror -o tools/verify/verify tools/verify/verify.c
	tools/verify/check_all.sh

lean-rapido: ## Compila só a biblioteca Lean padrão (precisa de elan/lake; baixa o cache do Mathlib)
	lake exe cache get
	lake build

higiene: ## Higiene do repo: arquivos grandes, JSON, caminhos de máquina, segredos
	$(PY) -m pytest -q tests/test_repo_higiene.py
