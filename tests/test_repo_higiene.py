"""Higiene do repositório: regras que não dependem de alguém lembrar.

Cada teste descreve a falha que impede. Só olha arquivos VERSIONADOS (git ls-files):
o que está solto no disco não entra no repo e não é problema daqui.
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_BYTES = 5 * 1024 * 1024

# Exceções ao limite de 5 MB, com motivo. Hoje o maior arquivo versionado tem ~2 MB,
# então a lista é vazia: adicionar aqui exige justificar no PR, e o teto só desce.
EXCECOES_TAMANHO: dict[str, str] = {}

# Diretórios cujo JSON é dado de pesquisa e tem de ser parseável.
DIRS_JSON = ("ledger/", "data/structured/", "verification/")
# Código nosso: nada de caminho da máquina de quem escreveu.
DIRS_SEM_CAMINHO = ("scripts/", "tools/", "infinito/", "evaluators/")

# Montados em pedaços para este arquivo não casar consigo mesmo.
PADROES_SEGREDO = {
    "chave privada": re.compile("-----BEGIN [A-Z ]*PRIVATE" + " KEY-----"),
    "token do GitHub": re.compile("gh[pousr]" + r"_[A-Za-z0-9]{30,}"),
    "chave AWS": re.compile("AK" + r"IA[0-9A-Z]{16}"),
    "chave sk-": re.compile(r"(?<![A-Za-z0-9])s" + r"k-[A-Za-z0-9_-]{20,}"),
}
CAMINHO_MAQUINA = re.compile(r"/home/[A-Za-z_][\w.-]*|/Users/[A-Za-z_][\w.-]*|Path\.home\(\)")


def _versionados() -> list[str]:
    try:
        saida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, check=True,
                               capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("fora de um checkout git: sem lista de arquivos versionados")
    return [p for p in saida.decode().split("\0") if p and (RAIZ / p).is_file()]


def _texto(rel: str) -> str | None:
    dados = (RAIZ / rel).read_bytes()
    if b"\0" in dados[:8192]:
        return None  # binário (gz, png, ...)
    return dados.decode("utf-8", errors="replace")


def test_nenhum_arquivo_versionado_passa_de_5_mb():
    grandes = {p: (RAIZ / p).stat().st_size for p in _versionados()
               if (RAIZ / p).stat().st_size > LIMITE_BYTES and p not in EXCECOES_TAMANHO}
    assert not grandes, f"arquivos > 5 MB sem exceção justificada: {grandes}"


def test_excecoes_de_tamanho_apontam_para_arquivos_que_existem():
    # Exceção órfã é lixo: o teto só desce.
    orfas = [p for p in EXCECOES_TAMANHO if p not in set(_versionados())]
    assert not orfas, f"exceções de tamanho para arquivo que não existe mais: {orfas}"


def test_todo_json_de_dados_e_valido():
    invalidos = {}
    for p in _versionados():
        if p.endswith(".json") and p.startswith(DIRS_JSON):
            try:
                json.loads((RAIZ / p).read_text(encoding="utf-8"))
            except ValueError as e:
                invalidos[p] = str(e)[:120]
    assert not invalidos, f"JSON inválido em dados versionados: {invalidos}"


def test_codigo_nosso_nao_tem_caminho_de_maquina():
    achados = []
    for p in _versionados():
        if p.startswith(DIRS_SEM_CAMINHO) and (t := _texto(p)) is not None:
            for n, linha in enumerate(t.splitlines(), 1):
                if CAMINHO_MAQUINA.search(linha):
                    achados.append(f"{p}:{n}")
    assert not achados, f"caminho de máquina (use variável de ambiente ou caminho relativo): {achados}"


@pytest.mark.parametrize("nome", sorted(PADROES_SEGREDO))
def test_nenhum_arquivo_versionado_contem_segredo(nome):
    achados = []
    for p in _versionados():
        if p == "tests/test_repo_higiene.py":
            continue
        t = _texto(p)
        if t is not None and PADROES_SEGREDO[nome].search(t):
            achados.append(p)  # só o caminho: nunca imprimir o valor
    assert not achados, f"padrão de {nome} em: {achados}"


def test_o_detector_de_caminho_de_maquina_pega_caminho_de_verdade():
    # Sem isto, regex quebrada deixaria os testes acima passarem em vão.
    assert CAMINHO_MAQUINA.search("open('/home/fulano/x')")
    assert CAMINHO_MAQUINA.search("Path.home() / 'x'")
    assert not CAMINHO_MAQUINA.search("/usr/include/x86_64-linux-gnu")


def test_o_detector_de_segredo_pega_formatos_conhecidos():
    assert PADROES_SEGREDO["token do GitHub"].search("gh" + "p_" + "a" * 36)
    assert PADROES_SEGREDO["chave AWS"].search("AK" + "IA" + "A" * 16)
    assert PADROES_SEGREDO["chave privada"].search("-----BEGIN RSA PRIVATE" + " KEY-----")
    assert not PADROES_SEGREDO["chave sk-"].search("task-force-de-teste-curto") and not PADROES_SEGREDO["chave sk-"].search("x sk-" + "a" * 4) and PADROES_SEGREDO["chave sk-"].search("k=sk-" + "a" * 30)


def test_dependabot_nao_sobe_a_serie_do_mcp_que_remove_o_fastmcp_do_servidor():
    """O primeiro PR do Dependabot (#33) pedia mcp>=2.2.0, e a 2.x remove `mcp.server.fastmcp`."""
    raiz = Path(__file__).resolve().parents[1]
    reqs = (raiz / "infinito" / "requirements.txt").read_text()
    assert any(l.startswith("mcp") and "<2" in l for l in reqs.splitlines()), "o servidor precisa do mcp 1.x"
    dep = (raiz / ".github" / "dependabot.yml").read_text()
    assert 'dependency-name: "mcp"' in dep and "version-update:semver-major" in dep
