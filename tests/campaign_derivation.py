"""Derivações compartilhadas pelos testes da campanha `covering-codes`: tudo sai de data/codes, do lakefile.toml e dos .lean, NUNCA de contagem digitada.

Um código novo no main (arquivo em data/codes) ou um teorema novo no lakefile entra sozinho na expectativa dos testes; o que a campanha não registrar passa a FALHAR
em vez de ficar de fora porque alguém esqueceu de atualizar um número.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMP = os.path.join(ROOT, "campaigns", "covering-codes")


def _ler(*partes):
    with open(os.path.join(ROOT, *partes), encoding="utf-8") as fh:
        return fh.read()


def codigos_de_data_codes():
    """[(q, n, R, M)] de cada data/codes/q*_n*_R*_M*.txt."""
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, "data", "codes"))):
        m = re.fullmatch(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt", f)
        if m:
            out.append(tuple(int(x) for x in m.groups()))
    return out


def raizes_da_lib(nome):
    """Módulos listados em `roots` da [[lean_lib]] `nome` do lakefile.toml."""
    m = re.search(rf'name = "{nome}".*?roots = \[([^\]]*)\]', _ler("lakefile.toml"), re.S)
    return re.findall(r'"([\w.]+)"', m.group(1)) if m else []


def tags_syn():
    """Tags M dos módulos CoveringLean.Syn_K<M> da lib CoveringSyn."""
    return [int(x) for x in re.findall(r"CoveringLean\.Syn_K(\d+)", " ".join(raizes_da_lib("CoveringSyn")))]


def teoremas_kernel_dos_finais():
    """Teoremas `K<q>_<n>_<R>_le_<M>_kernel` dos arquivos CoveringLean/K3_K*_Final.lean."""
    out = set()
    for p in glob.glob(os.path.join(ROOT, "CoveringLean", "K3_K*_Final.lean")):
        with open(p, encoding="utf-8") as fh:
            out |= set(re.findall(r"^theorem (K\d+_\d+_\d+_le_\d+_kernel)", fh.read(), re.M))
    return out


def teoremas_syn():
    """Teoremas `K<q>_<n>_<R>_le_<M>_syn` dos módulos da lib CoveringSyn."""
    out = set()
    for m in tags_syn():
        out |= set(re.findall(rf"^theorem (K\d+_\d+_\d+_le_{m}_syn)\b", _ler("CoveringLean", f"Syn_K{m}.lean"), re.M))
    return out


# teoremas "de manchete" do main que NÃO são cota de um código de data/codes: (arquivo, regex do nome). K_2(6,1)=12 (CoveringHeavy) e K_7(4,2) (v0.7).
OUTROS_DECLARADOS = (("CoveringLean/SearchK6ge12.lean", r"SC\.K_2_6_1_eq12"), ("CoveringLean/K742_Upper.lean", r"K_7_4_2_le_19"),
                     ("CoveringLean/K742_Final.lean", r"K_7_4_2_eq_19_of"), ("CoveringLean/LratK_K4.lean", r"refut6"), ("CoveringLean/K742Sat/P64.lean", r"refut18_p64"))


def teoremas_declarados_no_main():
    """{nome curto do teorema} que o main declara como resultado: Syn_K*, K*_kernel, e os OUTROS_DECLARADOS. Cada um exige registro formal na campanha."""
    nomes = teoremas_syn() | teoremas_kernel_dos_finais()
    for arq, rx in OUTROS_DECLARADOS:
        achou = re.findall(rf"^theorem ({rx})\b", _ler(*arq.split("/")), re.M)
        assert achou, f"{arq}: teorema {rx} sumiu do main; atualize OUTROS_DECLARADOS"
        nomes |= {x.split(".")[-1] for x in achou}
    return nomes


def estado_esperado_de_claim_de_cota(claim_id):
    """Estado que as guardas dão a um claim `<célula>-ub-<M>` de data/codes: PROVED se há teorema por síndromes (Lean medido + 2 componentes independentes),
    senão INDEPENDENTLY_REPRODUCED (só prefixos, declarado/relatado: a guarda de formal não o aceita). Derivado do lakefile e dos .lean, não digitado."""
    m = int(claim_id.rsplit("-ub-", 1)[1])
    return "PROVED" if m in set(tags_syn()) else "INDEPENDENTLY_REPRODUCED"
