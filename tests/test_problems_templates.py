"""Os templates do GitHub pedem exatamente os campos do Cartão de Problema."""
import re
import sys

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "problems"))
import validate  # noqa: E402

TPL = RAIZ / ".github" / "ISSUE_TEMPLATE"


def _ids(nome):
    return re.findall(r"^    id: (\w+)$", (TPL / nome).read_text(encoding="utf-8"), re.M)


def test_proposta_nao_pede_campo_que_o_cartao_nao_tem_nem_esquece_um_obrigatorio():
    ids = set(_ids("proposta-de-problema.yml")) - {"confirmacoes"}
    # campos de objeto aninhado viram <objeto>_<campo>
    esperado = {"id", "titulo", "dominio", "tipo", "enunciado", "enunciado_formal", "celula_ledger",
                "melhor_conhecido_valor", "melhor_conhecido_fonte", "melhor_conhecido_ref",
                "avaliador_id", "avaliador_como_rodar", "avaliador_custo_estimado_usd"}
    assert ids == esperado
    # todo campo obrigatório do cartão (exceto o que o sistema preenche) está no formulário
    cartao = validate.OBRIGATORIOS - {"formato", "estado", "nosso", "historico", "melhor_conhecido", "avaliador"}
    assert cartao <= ids


def test_opcoes_de_tipo_do_formulario_sao_as_do_validador():
    txt = (TPL / "proposta-de-problema.yml").read_text(encoding="utf-8")
    opcoes = re.search(r"options: \[(.*?)\]", txt)[1].split(", ")
    assert tuple(opcoes) == validate.TIPOS


def test_submissao_pede_artefato_hash_e_saida_do_avaliador():
    ids = set(_ids("submissao-de-candidato.yml"))
    assert {"id", "nosso_valor", "artefato", "sha256", "avaliador_como_rodar", "avaliador_saida"} <= ids


def test_issues_em_branco_ficam_desligadas_e_o_pr_pede_risco_e_closes():
    assert "blank_issues_enabled: false" in (TPL / "config.yml").read_text(encoding="utf-8")
    pr = (RAIZ / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    assert re.search(r"^Risco: baixo\|médio\|alto — motivo$", pr, re.M) and "Closes #N" in pr
    for secao in ("O que mudou", "Por quê", "Como validei", "O que ficou de fora"):
        assert f"## {secao}" in pr


def test_exemplo_do_readme_roda_e_produz_cartao_valido(tmp_path):
    import shutil
    import subprocess
    txt = (RAIZ / "problems" / "README.md").read_text(encoding="utf-8")
    codigo = re.search(r"python3 - <<'PY'\n(.*?)\nPY\n", txt, re.S)[1]
    for rel in ("problems", "tools/problems"):
        shutil.copytree(RAIZ / rel, tmp_path / rel)
    subprocess.run([sys.executable, "-c", codigo], cwd=tmp_path, check=True)
    novo = tmp_path / "problems/cartoes/cobertura-k7-9-5-ub.json"
    assert novo.exists()
    r = subprocess.run([sys.executable, "tools/problems/validate.py", str(novo)], cwd=tmp_path,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
