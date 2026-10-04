"""Amarras entre o Lean de K_7(4,2) e os scripts Python (docs/exatos/LEAN_K742.md).

O kernel confere sozinho que a CNF do gerador Lean (`K742Cnf.cnf`) é a do DIMACS lido (`checkF`
e `listsBeq` em `lratk_refute`), então um erro aqui não deixa passar teorema falso; estes
testes só pegam cedo (sem Lean, em segundos) uma divergência que faria o build falhar:

* a lista `perfis18` de `CoveringLean/K742_Cnf.lean` é a de `encode.perfis(7, 18)`, na mesma
  ordem (os índices dos perfis nos dados e nos teoremas dependem disso);
* os perfis de `CoveringLean/LratK_K4.lean` são os de `encode.perfis(4, 6)`;
* os CNFs guardados em `CoveringLean/LratK_K4/` e o sha256 de `manifesto.json` são exatamente o
  que `encode.py` gera hoje;
* nenhum arquivo Lean novo usa `sorry`, `native_decide`, `ofReduceBool` ou `implemented_by`.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "exatos" / "k742"))

import encode  # noqa: E402

LEAN = RAIZ / "CoveringLean"
NOVOS = ["K742_Upper.lean", "K742_Fibras.lean", "K742_Cnf.lean", "K742_Final.lean", "LratK.lean",
         "LratKData.lean", "LratK_K4.lean", "K742Sat/P64.lean", "K742_PonteCnf.lean",
         "K742_Ponte.lean", "K742_Eq19.lean", "K742Sat/Refut.lean", "LratKFinal.lean"] + sorted(
    str(f.relative_to(RAIZ / "CoveringLean")) for f in (RAIZ / "CoveringLean" / "K742Sat").glob("S*/*.lean"))


def perfis_do_lean(texto, nome):
    corpo = texto.split(f"def {nome}")[1].split(":=", 1)[1]
    corpo = corpo.split("\n\n")[0]
    tipos = re.findall(r"\[([\d,\s]+)\]", corpo)
    ts = [tuple(int(x) for x in t.replace(" ", "").split(",")) for t in tipos]
    return [tuple(ts[i:i + 4]) for i in range(0, len(ts), 4)]


def test_perfis18_do_lean_sao_os_do_encode_na_mesma_ordem():
    lean = perfis_do_lean((LEAN / "K742_Cnf.lean").read_text(), "perfis18")
    assert lean == encode.perfis(7, 18)
    assert len(lean) == 70


def test_perfis6_do_teste_k4_sao_os_do_encode_na_mesma_ordem():
    lean = perfis_do_lean((LEAN / "LratK_K4.lean").read_text(), "perfis6")
    assert lean == encode.perfis(4, 6)


def test_cnfs_guardados_e_manifesto_conferem_com_o_encode_de_hoje():
    man = json.loads((RAIZ / "tools" / "exatos" / "k742" / "lean" / "manifesto.json").read_text())
    assert man, "manifesto vazio"
    for e in man:
        ps = encode.perfis(e["q"], e["M"])
        p = ps[e["perfil"]]
        assert ["".join(map(str, t)) for t in p] == e["tipos"]
        cnf, _, _ = encode.codificar(e["q"], e["M"], p)
        txt = cnf.dimacs([f"K_{e['q']}(4,2) M={e['M']} perfil {e['perfil']}: {p}"])
        assert hashlib.sha256(txt.encode()).hexdigest() == e["sha256.cnf"]
        if e["q"] == 4:
            nome = LEAN / "LratK_K4" / f"K4_4_2_M6_p{e['perfil']:04d}"
            assert nome.with_suffix(".cnf").read_text() == txt
            lrat = nome.with_suffix(".lrat").read_bytes()
            assert hashlib.sha256(lrat).hexdigest() == e["sha256.lrat"]
            assert b" d " not in lrat


def test_lean_novo_sem_atalhos_fora_do_kernel():
    proibidos = ["sorry", "native_decide", "ofReduceBool", "implemented_by", "decide := true"]
    for f in NOVOS:
        texto = (LEAN / f).read_text()
        # comentários e docstrings podem citar os nomes; só o código conta
        codigo = re.sub(r"/-.*?-/", "", texto, flags=re.S)
        codigo = re.sub(r"--[^\n]*", "", codigo)
        for p in proibidos:
            assert p not in codigo, f"{p} em {f}"
        if re.search(r"^theorem ", codigo, flags=re.M):
            assert "#print axioms" in texto, f"sem #print axioms em {f}"


def _semquebra():
    caminho = RAIZ / "tools" / "exatos" / "k742" / "lean" / "semquebra_M18.jsonl"
    return {e["perfil"]: e for e in map(json.loads, caminho.read_text().splitlines())}


def test_semquebra_tem_os_70_perfis_com_a_cnf_do_encode_de_hoje():
    reg = _semquebra()
    ps = encode.perfis(7, 18)
    assert sorted(reg) == list(range(70))
    for p, e in reg.items():
        assert e["quebra"] is False
        assert ["".join(map(str, t)) for t in ps[p]] == e["tipos"]
        cnf, _, _ = encode.codificar(7, 18, ps[p], quebra=False)
        txt = cnf.dimacs([f"K_7(4,2) M=18 perfil {p} sem quebra: {ps[p]}"])
        assert hashlib.sha256(txt.encode()).hexdigest() == e["sha256.cnf"]
        assert e["sha256.arquivos"]["f.cnf"] == e["sha256.cnf"]
        assert e["K"] == e["n"] + e["passos"]
        assert sum(m["dicas"] for m in e["modulos"]) == e["dicas"]


def test_modulos_gerados_batem_com_o_registro_e_a_lista_de_perfis():
    reg = _semquebra()
    ps = encode.perfis(7, 18)
    sat = LEAN / "K742Sat"
    for p, e in reg.items():
        d = sat / f"S{p}"
        bs = sorted(f.name for f in d.glob("B*.lean"))
        assert bs == sorted(f"B{m['modulo']}.lean" for m in e["modulos"])
        final = (d / "Final.lean").read_text()
        tl = "[" + ", ".join("[" + ",".join(map(str, t)) + "]" for t in ps[p]) + "]"
        assert f"cnfSemQuebra 7 18 {tl}" in final
        assert f"#print axioms K742Sat.s{p}.unsatFor" in final
    refut = (sat / "Refut.lean").read_text()
    for p in range(70):
        assert f"import CoveringLean.K742Sat.S{p}.Final" in refut
        assert f"exact K742Sat.s{p}.unsatFor" in refut


def test_registro_das_vms_tem_todo_modulo_compilado_com_os_axiomas_permitidos():
    """O log de execução (logs das VMs, copiados para tools/exatos/k742/lean/execucao/) mostra
    rc = 0 para cada módulo e `#print axioms` de cada `unsatFor` sem nada além dos três axiomas
    padrão."""
    ex = RAIZ / "tools" / "exatos" / "k742" / "lean" / "execucao"
    mods = {}
    for f in sorted(ex.glob("modulos*.jsonl")):
        for e in map(json.loads, f.read_text().splitlines()):
            if e["rc"] == 0:
                mods[e["modulo"]] = e
    reg = _semquebra()
    for p, e in reg.items():
        esperados = [f"CoveringLean.K742Sat.S{p}.Data", f"CoveringLean.K742Sat.S{p}.Final"] + [
            f"CoveringLean.K742Sat.S{p}.B{m['modulo']}" for m in e["modulos"]]
        for m in esperados:
            assert m in mods, f"{m} sem registro de compilação com rc 0"
    ax = (ex / "axiomas.txt").read_text().splitlines()
    for p in range(70):
        linha = [ln for ln in ax if f"'K742Sat.s{p}.unsatFor'" in ln]
        assert linha, f"sem #print axioms do perfil {p}"
        assert linha[0].endswith("depends on axioms: [propext, Classical.choice, Quot.sound]")
