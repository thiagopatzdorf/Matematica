"""Livro de afirmações da campanha de compressão: nada entra sem o tipo certo de prova, e o gabarito não vaza para os métodos."""
import hashlib
import json
import re

from conftest import RAIZ

BASE = RAIZ / "tools" / "fatoracao" / "baseline"
CLAIMS = [json.loads(x) for x in (BASE / "claims.jsonl").read_text(encoding="utf-8").splitlines()]
STATUS = {"PROVADO", "VERIFICADO", "EVIDENCIA", "HIPOTESE"}
CAMPANHA = (RAIZ / "docs" / "fatoracao" / "campanha-compressao.md").read_text(encoding="utf-8")


def _teste_existe(ref):
    caminho, _, nome = ref.partition("::")
    arquivo = RAIZ / caminho
    return arquivo.is_file() and re.search(rf"^def {re.escape(nome)}\(", arquivo.read_text(encoding="utf-8"), flags=re.M) is not None


def test_afirmacao_com_status_fora_dos_quatro_ou_id_repetido():
    ids = [c["id"] for c in CLAIMS]
    assert len(ids) == len(set(ids))
    assert all(c["status"] in STATUS and c["enunciado"].strip() for c in CLAIMS)


def test_provado_sem_fonte_lida_vira_afirmacao_de_ouvir_dizer():
    for c in CLAIMS:
        if c["status"] == "PROVADO":
            assert c.get("fonte") and c.get("leitura") in ("lido", "resumo") and c.get("limite"), c["id"]


def test_verificado_sem_teste_que_exista_nao_e_reproduzivel():
    for c in CLAIMS:
        if c["status"] == "VERIFICADO":
            assert c.get("teste") and _teste_existe(c["teste"]), c["id"]
            if "comando" in c:
                assert re.fullmatch(r"[0-9a-f]{40}", c.get("commit_cado", "")), c["id"]


def test_evidencia_sem_limite_declarado_vale_mais_do_que_deveria():
    for c in CLAIMS:
        if c["status"] == "EVIDENCIA":
            assert c.get("dados") and c.get("limite"), c["id"]
            if "sha256_dados" in c:
                arquivo = RAIZ / c["dados"]
                assert hashlib.sha256(arquivo.read_bytes()).hexdigest() == c["sha256_dados"], c["id"]


def test_hipotese_que_nada_poderia_derrubar_nao_e_hipotese():
    for c in CLAIMS:
        if c["status"] == "HIPOTESE":
            assert c.get("falsifica") and re.fullmatch(r"E\d", c.get("experimento", "")), c["id"]
            assert re.search(rf"\*\*{re.escape(c['experimento'])}\b", CAMPANHA), f"{c['experimento']} não está no registro de experimentos"


def test_livro_de_afirmacoes_que_faz_alegacao_sobre_p_igual_np_ou_rsa_geral():
    texto = " ".join(c["enunciado"] for c in CLAIMS).lower().replace(" ", "")
    assert "p=np" not in texto and "quebrageral" not in texto and "rsa-2048" not in texto


def test_metodo_novo_que_le_o_gabarito_do_recorde_ou_os_fatores():
    """Código de método (tools/fatoracao/metodos/) não pode abrir baseline/, nem citar fatores ou o polinômio publicado."""
    proibido = ("baseline", "rsa896", "numeros.json", "claims.jsonl")
    for arquivo in (RAIZ / "tools" / "fatoracao" / "metodos").rglob("*.py"):
        texto = arquivo.read_text(encoding="utf-8").lower()
        assert not any(p in texto for p in proibido), f"{arquivo.name} aponta para o gabarito"
