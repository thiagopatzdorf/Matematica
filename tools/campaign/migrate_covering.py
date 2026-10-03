#!/usr/bin/env python3
"""Refaz do zero a campanha `covering-codes` (campaigns/covering-codes/) a partir dos artefatos deste repositório.

    python3 tools/campaign/migrate_covering.py --factory-src <pasta src da Fábrica> [--sem-lean] [--sem-corridas]
    FACTORY_SRC=<pasta src> python3 tools/campaign/migrate_covering.py

Usa o pacote `factory_cauteloso.matematica` (store, claims, verify, formal, literature, coverage). Idempotente: apaga só o que o
armazenamento da campanha criou (campaign.json, audit/, reproduce.json, reports/ e as pastas de registros) e preserva
`_fatos/` (fatos medidos à mão) e `artifacts/` (regenerado aqui). Nada é inventado: toda corrida de verificador, de busca e de Lean é
executada de verdade por este script; o que não dá para executar aqui entra como registro "declarado, não reproduzido".

Decisões de honestidade (explicadas nos registros):
  * claim nasce IDEA por `agente-c`; as promoções são feitas pelo ator `migrate_covering.py` (um programa, outro ator que o autor do
    claim), SEMPRE pelas guardas de `claims.mudar_estado`: se a guarda nega, o claim fica onde a evidência o deixa;
  * contrato de verificação (red team D-10/D-11/D-12, Pilot-v2 2026-10-03): witnesses declaram `parameters` {q,n,R,M}; o claim declara os mesmos em
    `scope.parameters` (M = `bound.value`); os dois verificadores recebem os parâmetros por `{param:NOME}` e NÃO leem o nome do arquivo; cada
    verificador registra o autor REAL (`implemented_by`). Se a guarda de INDEPENDENTLY_REPRODUCED nega (hoje: o 2º verificador foi escrito por quem
    criou os claims), o claim fica em EMPIRICAL com os motivos em `blocked_independently_reproduced`: nada é forçado;
  * FORMALLY_VERIFIED nunca é pedido de fato: exige `statement_review` de um revisor que não seja o autor e ninguém revisou os
    enunciados (README: "revisão humana"). Os motivos exatos da guarda ficam em `formal_verification_blockers` de cada claim;
  * os teoremas pesados (CoveringHeavy, ~12,4 h de CPU) não são compilados aqui: o registro formal deles guarda os axiomas declarados
    em `declared_axioms`, com `axioms: null`, e NÃO sustenta promoção.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAMPANHA = "covering-codes"
AUTOR = "agente-c"
PROMOTOR = "migrate_covering.py"
CELULAS = {  # (q, n, R) -> arquivo do melhor código verificado em data/codes
    "k5-7-2": (5, 7, 2), "k4-10-4": (4, 10, 4), "k5-9-3": (5, 9, 3), "k5-10-4": (5, 10, 4), "k5-9-5": (5, 9, 5),
    "k5-9-4": (5, 9, 4), "k7-8-3": (7, 8, 3), "k7-9-4": (7, 9, 4), "k2-6-1": (2, 6, 1),
}
LB_ESFERA = {"k5-7-2": 215, "k4-10-4": 51, "k5-9-3": 327, "k5-10-4": 158, "k5-9-5": 12, "k5-9-4": 52, "k7-8-3": 439, "k7-9-4": 221}
# código -> (célula, M, em README/paper?) ; M do melhor verificado em data/codes
CODIGOS = [
    ("k5-7-2", 500, True), ("k4-10-4", 192, True), ("k5-9-3", 1250, True), ("k5-10-4", 625, True),
    ("k5-9-5", 50, True), ("k5-9-4", 250, True), ("k7-8-3", 1893, True), ("k7-8-3", 1887, False),
    ("k7-9-4", 1351, True), ("k7-9-4", 1285, False),
]
KERI_PREVIO = {"k5-7-2": 525, "k4-10-4": 208, "k5-9-3": 1275, "k5-10-4": 875, "k5-9-5": 55, "k5-9-4": 255, "k7-8-3": 2337}
AXIOMAS_DECLARADOS = ["propext", "Classical.choice", "Quot.sound"]
# Autor do verify_cover_dilation.py: o agente que o escreveu NESTA campanha (primeira sessão, commit 483a6c5 assinado "Claude"; na campanha esse agente
# é `agente-c`, o mesmo que cria os claims). Registrar outro nome seria inventar autor; a guarda de independência reprova e isso é um achado.
AUTOR_DILATACAO = AUTOR
# Autor do verify-rust: o agente "Verif-Rust" desta sessão, que recebeu só a especificação do problema e docs/code-format.md (não leu verify.c nem o
# verificador em Python): independência de autoria e de lógica declarada em tools/verify-rust/README.md.
AUTOR_RUST = "agente-verif-rust"
# Quem modificou os dois verificadores para aceitar parâmetros explícitos (2026-10-03): fica nas notas, não em `implemented_by` (autor original).
MODIFICADO_POR = "agente-pilot-v2"
PARAMS_CMD = ["--q", "{param:q}", "--n", "{param:n}", "--R", "{param:R}", "--M", "{param:M}"]


def autor_do_arquivo(rel: str) -> str:
    """Autor do primeiro commit do arquivo (`git log`): é o autor REAL do verificador, não um nome que escolhemos."""
    r = subprocess.run(["git", "log", "--follow", "--diff-filter=A", "--format=%an", "--", rel], cwd=REPO, capture_output=True, text=True)
    nomes = [x.strip() for x in r.stdout.splitlines() if x.strip()]
    if r.returncode != 0 or not nomes:
        raise SystemExit(f"erro: não achei o autor de {rel} no git log (o implemented_by do verificador não pode ser inventado)")
    return nomes[-1]


def ancorar_campanha(c, ator: str) -> dict:
    """`Campanha.ancorar` (= campaign_anchor) + um `campaign.update` logo depois.

    Por quê o update: `report.campaign_audit` toma o ÚLTIMO evento de kind=campaign como o registro de campaign.json e não ignora o evento
    `campaign.anchor` (marcado sem_registro), então qualquer âncora gravada depois do último update faz a auditoria acusar, em falso,
    "campaign.json editado fora das ferramentas" (medido em 2026-10-03: integra=false sem edição nenhuma). Defeito da infraestrutura
    (report.py, filtro `not e.get("sem_registro")`), não consertado aqui; o update devolve a coerência e registra qual âncora foi tirada.
    Sem GENESIS_MATH_ANCHOR_KEY o HMAC fica null (nenhum segredo é inventado)."""
    a = c.ancorar(ator, "COORDINATOR")
    c.atualizar_meta(ator, "COORDINATOR", last_anchor={"seq": a["seq"], "hash": a["hash"], "hmac": a["hmac"], "ts": a["ts"]})
    return a


def cel_de(q: int, n: int, r: int) -> str | None:
    return next((k for k, v in CELULAS.items() if v == (q, n, r)), None)


def nome_codigo(cel: str, m: int) -> str:
    q, n, r = CELULAS[cel]
    return f"q{q}_n{n}_R{r}_M{m}"


def wid(cel: str, m: int) -> str:
    return "w-" + nome_codigo(cel, m).lower().replace("_", "-")


def sha_bytes(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonico(p: Path) -> str:
    ws = sorted(ln for ln in p.read_text().split("\n") if ln.strip())
    return hashlib.sha256(("\n".join(ws) + "\n").encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--factory-src", default=os.environ.get("FACTORY_SRC"), help="pasta src que contém factory_cauteloso/")
    ap.add_argument("--sem-lean", action="store_true", help="não roda lake build / #print axioms (registros formais ficam NOT_RUN)")
    ap.add_argument("--sem-corridas", action="store_true", help="registra tudo mas não executa verificadores nem buscas")
    ap.add_argument("--so-ancorar", action="store_true", help="NÃO refaz nada: só ancora a cabeça atual da cadeia (use depois de reproduce/auditar)")
    a = ap.parse_args()
    if not a.factory_src:
        print("erro: informe --factory-src ou FACTORY_SRC", file=sys.stderr)
        return 2
    sys.path.insert(0, str(Path(a.factory_src).resolve()))
    from factory_cauteloso.matematica import claims as K, coverage as COV, formal as F, literature as L, verify as V  # noqa: E402
    from factory_cauteloso.matematica.model import TransicaoNegada, checar_transicao, validar_registro_formal  # noqa: E402
    from factory_cauteloso.matematica.store import Campanha, sha256_arquivo  # noqa: E402

    raiz = REPO / "campaigns" / CAMPANHA
    if a.so_ancorar:
        print(json.dumps(ancorar_campanha(Campanha(raiz), PROMOTOR), ensure_ascii=False, indent=1))
        return 0
    # ------------------------------------------------------------------ zera só o que o armazenamento criou
    for nome in ("campaign.json", "audit", "reproduce.json", "reports", "artifacts", "claims", "experiments", "witnesses", "counterexamples",
                 "structures", "reductions", "transfer", "families", "residuals", "formal", "verifiers", "verifier_runs", "literature",
                 "reports", "provenance"):
        p = raiz / nome
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    raiz.mkdir(parents=True, exist_ok=True)
    c = Campanha.criar(raiz, CAMPANHA, "Covering codes: campanha piloto (cotas de esfera, K_2(6,1), K_7(9,4) e outros códigos)",
                       ator=AUTOR, papel="COORDINATOR", data_root="../..", domain="covering codes K_q(n,R)",
                       lean_toolchain=(REPO / "lean-toolchain").read_text().strip())
    commit = V.commit_do_repo(REPO)

    def gravar(tipo, rid, reg, papel="PROPOSER", ator=AUTOR):
        return c.gravar(tipo, rid, reg, ator=ator, papel=papel, permitir_sobrescrever=False)

    # ------------------------------------------------------------------ artefato derivado: o código de 12 palavras do Lean
    lean_a6c = (REPO / "CoveringLean/A6c_Search.lean").read_text()
    m12 = re.search(r"def code12.*?\(\(\[([0-9, ]+)\] : List", lean_a6c, re.S)
    enc12 = [int(x) for x in m12.group(1).split(",")]
    (raiz / "artifacts").mkdir(exist_ok=True)
    art12 = raiz / "artifacts" / "q2_n6_R1_M12.txt"
    art12.write_text("\n".join("".join(str((k // 2 ** i) % 2) for i in range(6)) for k in enc12) + "\n")

    # ------------------------------------------------------------------ verificadores
    autor_c = autor_do_arquivo("tools/verify/verify.c")
    V.registrar_verificador(c, "verify-c", language="c", source_files=["tools/verify/verify.c"], independence_group="c-ballmark-verify.c",
                            command=["{workdir}/verify", *PARAMS_CMD, "{witness}"], fail_exit_codes=[1, 2], timeout_s=120, ator=AUTOR, papel="PROPOSER",
                            implemented_by=autor_c,
                            build=[["cc", "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", "{workdir}/verify", "tools/verify/verify.c"]])
    V.registrar_verificador(c, "verify-py-dilation", language="python", source_files=["tools/campaign/verify_cover_dilation.py"],
                            independence_group="python-numpy-dilation", fail_exit_codes=[1, 2], timeout_s=300, ator=AUTOR, papel="PROPOSER",
                            implemented_by=AUTOR_DILATACAO,
                            command=["python3", "tools/campaign/verify_cover_dilation.py", *PARAMS_CMD, "{witness}"])
    # 3º verificador (2026-10-03): escrito por OUTRO agente que não leu os dois anteriores (tools/verify-rust/README.md declara o que leu).
    V.registrar_verificador(c, "verify-rust", language="rust", source_files=["tools/verify-rust/src/main.rs", "tools/verify-rust/Cargo.toml"],
                            independence_group="rust-layered-dilation", fail_exit_codes=[1, 2], timeout_s=300, ator=AUTOR, papel="PROPOSER",
                            implemented_by=AUTOR_RUST, command=["{workdir}/verify-rust", *PARAMS_CMD, "{witness}"],
                            build=[["cargo", "build", "--release", "--offline", "--manifest-path", "tools/verify-rust/Cargo.toml",
                                    "--target-dir", "{workdir}/rust-target"],
                                   ["cp", "{workdir}/rust-target/release/verify-rust", "{workdir}/verify-rust"]])
    contrato = (f" Contrato de saída: 0 cobre, 1 ponto descoberto, 2 o witness contradiz os parâmetros (FAIL = fail_exit_codes [1, 2]); 3 uso/falha operacional "
                f"(ERROR, nunca FAIL). Recebe q,n,R,M por {{param:NOME}} e rejeita nome de arquivo que diga outra instância. Modificado em 2026-10-03 por "
                f"{MODIFICADO_POR} (parâmetros explícitos); o autor original (implemented_by) segue o do git log.")
    for vid, nota in (("verify-rust", "Escrito por outro agente (agente-verif-rust) sem ler os outros dois verificadores nem o gerador do formato; algoritmo de dilatação "
                       "por camadas com um byte por ponto (OR ao longo de cada reta de coordenada), O(R·n·q^n). Declaração de independência e do que foi lido em "
                       "tools/verify-rust/README.md. Independente em linguagem, código, algoritmo e autoria; NÃO em especificação do problema (a definição de código de cobertura é a mesma)."),
                      ("verify-c", f"Verificador oficial do repositório (marca bolas de raio R num bitset). Escrito antes desta campanha por {autor_c} "
                                   f"(autor do primeiro commit de tools/verify/verify.c)." + contrato),
                      ("verify-py-dilation", "Escrito NESTA campanha pelo mesmo agente que cria os claims (agente-c): independente em linguagem, código e algoritmo "
                       "(dilatação do indicador do código no grid, sem enumerar bolas), mas NÃO em autoria nem em especificação do formato. "
                       "Concorda com verify-c em positivos e negativos (tests/test_campaign_verifier.py). Por ter o mesmo autor dos claims, a guarda de "
                       "INDEPENDENTLY_REPRODUCED não conta este verificador (achado, não defeito)." + contrato)):
        r = c.ler("verifiers", vid)
        r["notes"] = nota
        c.gravar("verifiers", vid, r, ator=AUTOR, papel="PROPOSER", acao="verifiers.note")

    # ------------------------------------------------------------------ experimentos (executados de verdade)
    def exec_(args, cwd=REPO, t=300):
        return V.executar(args, cwd, t)

    corridas = not a.sem_corridas
    mirror = []
    if corridas:
        for args in (["6", "10"], ["6", "10", "2"], ["6", "11"]):
            r = exec_(["python3", "scripts/k261/sc_ref.py", *args])
            try:
                j = json.loads(r["stdout"])
            except ValueError:
                j = {"erro": "saída não é JSON"}
            mirror.append({"command": ["python3", "scripts/k261/sc_ref.py", *args], "rc": r["rc"], "ok": j.get("ok"), "nodes": j.get("nodes"),
                           "frontier_len": j.get("frontier_len"), "runtime_s": r["runtime_s"],
                           "output_sha256": hashlib.sha256(r["stdout"].encode()).hexdigest()})
    fonte_mirror = [{"path": "scripts/k261/sc_ref.py", "sha256": sha256_arquivo(REPO / "scripts/k261/sc_ref.py")}]
    gravar("experiments", "exp-k2-6-1-search-mirror", {
        "experiment_id": "exp-k2-6-1-search-mirror", "kind": "exhaustive",
        "description": "Busca exaustiva com poda do argumento K_2(6,1) >= 12 (WLOG a palavra 63 no código): espelho Python do SearchCore.chkN do Lean. "
                       "`6 10`: nenhuma cobertura com 11 palavras; `6 10 2`: 38 estados na fronteira (= os 38 G610_Chunk); controle positivo `6 11` acha cobertura de 12.",
        "ranges": {"q": 2, "n": 6, "R": 1, "espaco": "todas as 64 palavras", "palavra_fixa": 63, "centros_livres": 10, "profundidade_fronteira": 2},
        "implementation": "scripts/k261/sc_ref.py (COMPARTILHA a lógica do SearchCore.chkN: não é verificação independente do teorema Lean)",
        "source_files": fonte_mirror, "instances": ["k2-6-1"], "result": {"runs": mirror, "executado_neste_run": corridas},
        "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

    regen = {"executado_neste_run": False}
    if corridas:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "q7_n9_R4_M1285.txt"
            r = exec_(["python3", "scripts/search/gen.py", "data/search/p1285.json", str(out)])
            regen = {"executado_neste_run": True, "rc": r["rc"], "stdout": r["stdout"].strip(),
                     "sha256_regenerado": sha_bytes(out) if out.is_file() else None,
                     "sha256_witness": sha_bytes(REPO / "data/codes/q7_n9_R4_M1285.txt"),
                     "identico_byte_a_byte": out.is_file() and out.read_bytes() == (REPO / "data/codes/q7_n9_R4_M1285.txt").read_bytes()}
    gravar("experiments", "exp-k7-9-4-1285-regen", {
        "experiment_id": "exp-k7-9-4-1285-regen", "kind": "search",
        "description": "Regenera o código de 1285 palavras com o gerador versionado a partir de data/search/p1285.json.",
        "ranges": None, "implementation": "scripts/search/gen.py",
        "command": ["python3", "scripts/search/gen.py", "data/search/p1285.json", "<saída>"],
        "source_files": [{"path": p, "sha256": sha256_arquivo(REPO / p)} for p in ("scripts/search/gen.py", "data/search/p1285.json")],
        "instances": ["k7-9-4"], "result": regen, "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

    gravar("experiments", "exp-k7-9-4-1351-lincov", {
        "experiment_id": "exp-k7-9-4-1351-lincov", "kind": "search",
        "description": "Geração do código de 1351 palavras: 3 cosets de um núcleo [9,3]_7 (1029 palavras) pelo gerador `lincov` do repositório público "
                       "do Marosi (Mapika/coldcase, commit 56a8cce) + 322 palavras de remendo guloso. DECLARADO no README; NÃO reproduzível aqui: o "
                       "lincov não está neste repositório e a origem do remendo não foi registrada. O que é reproduzível é a estrutura (46 cosets de uma "
                       "reta, scripts/codes/structure.py) e a verificação do código final.",
        "ranges": None, "implementation": "lincov (Mapika/coldcase@56a8cce) + remendo guloso sem registro", "command": None,
        "source_files": [], "instances": ["k7-9-4"],
        "result": {"reproduzivel_aqui": False, "executado_neste_run": False, "declarado_em": "README.md:27-31; data/structured/q7_n9_R4_M1351.json"},
        "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

    gravar("experiments", "exp-prior-search-unrecorded", {
        "experiment_id": "exp-prior-search-unrecorded", "kind": "search",
        "description": "Buscas que produziram os códigos 192, 625, 500, 1250, 250, 50, 1893 (anteriores à v0.3: gerador, comando, seed e data não registrados "
                       "em data/structured/*.json) e o 1887 (VM lean-build2, 'maestro', sem comando registrado).",
        "ranges": None, "implementation": None, "command": None, "source_files": [], "instances": [],
        "result": {"reproduzivel_aqui": False, "executado_neste_run": False}, "repo_commit": commit, "created_by": AUTOR,
        "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

    est = {"executado_neste_run": False}
    if corridas:
        r = exec_(["python3", "scripts/codes/build_structured.py", "--check"])
        est = {"executado_neste_run": True, "rc": r["rc"], "tail": (r["stdout"] + r["stderr"]).strip()[-300:]}
    gravar("experiments", "exp-structure-regeneration", {
        "experiment_id": "exp-structure-regeneration", "kind": "symbolic",
        "description": "Regenera data/structured/*.json de data/codes/*.txt (detecta cosets) e compara com os versionados.",
        "ranges": None, "implementation": "scripts/codes/build_structured.py --check",
        "source_files": [{"path": p, "sha256": sha256_arquivo(REPO / p)} for p in ("scripts/codes/build_structured.py", "scripts/codes/structure.py", "scripts/codes/codefmt.py")],
        "instances": [], "result": est, "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

    # elo Lean <-> witness (calculado, não declarado)
    lean_data = (REPO / "CoveringLean/C1_Data_K7_9_4.lean").read_text()
    nums = [int(x) for x in re.findall(r"\d+", lean_data[lean_data.index("def K7_9_4"):].split(":=")[1])]
    pal = ["".join(str((w // 7 ** k) % 7) for k in range(9)) for w in nums]
    sha_lean = hashlib.sha256(("\n".join(sorted(pal)) + "\n").encode()).hexdigest()
    sha_w1351 = canonico(REPO / "data/codes/q7_n9_R4_M1351.txt")
    gravar("experiments", "exp-lean-data-equals-witness-1351", {
        "experiment_id": "exp-lean-data-equals-witness-1351", "kind": "symbolic",
        "description": "Decodifica a lista de C1_Data_K7_9_4.lean (base 7 little-endian) e compara o sha256 canônico com o do witness data/codes/q7_n9_R4_M1351.txt.",
        "ranges": None, "implementation": "regex + sha256 em tools/campaign/migrate_covering.py",
        "source_files": [{"path": "CoveringLean/C1_Data_K7_9_4.lean", "sha256": sha256_arquivo(REPO / "CoveringLean/C1_Data_K7_9_4.lean")}],
        "instances": ["k7-9-4"], "result": {"palavras": len(nums), "estritamente_crescente": nums == sorted(set(nums)), "todas_menores_que_7_9": max(nums) < 7 ** 9,
                                            "sha256_canonico_lean": sha_lean, "sha256_canonico_witness": sha_w1351, "iguais": sha_lean == sha_w1351,
                                            "executado_neste_run": True},
        "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

    # ------------------------------------------------------------------ witnesses
    descr_json = {}
    for cel, m, _ in CODIGOS:
        nome = nome_codigo(cel, m)
        p = REPO / "data/codes" / f"{nome}.txt"
        js = json.loads((REPO / "data/structured" / f"{nome}.json").read_text())
        produzido = {("k7-9-4", 1351): "exp-k7-9-4-1351-lincov", ("k7-9-4", 1285): "exp-k7-9-4-1285-regen"}.get((cel, m), "exp-prior-search-unrecorded")
        q, n, r = CELULAS[cel]
        descr_json[(cel, m)] = js
        gravar("witnesses", wid(cel, m), {
            "witness_id": wid(cel, m), "path": f"data/codes/{nome}.txt", "format": "covering-code/v1 (lista plana, uma palavra por linha)",
            "sha256": sha256_arquivo(p), "canonical_sha256": canonico(p), "canonical_sha256_declared_in_structured": js["canonical_sha256"],
            "structured_description": {"path": f"data/structured/{nome}.json", "sha256": sha256_arquivo(REPO / f"data/structured/{nome}.json")},
            "q": q, "n": n, "R": r, "M": m, "parameters": {"q": q, "n": n, "R": r, "M": m}, "produced_by": produzido, "claim_ids": [], "implementation": js["provenance"].get("generator"),
            "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")
    gravar("witnesses", "w-q2-n6-r1-m12", {
        "witness_id": "w-q2-n6-r1-m12", "path": "campaigns/covering-codes/artifacts/q2_n6_R1_M12.txt", "format": "covering-code/v1 (lista plana)",
        "sha256": sha256_arquivo(art12), "canonical_sha256": canonico(art12), "q": 2, "n": 6, "R": 1, "M": 12,
        "parameters": {"q": 2, "n": 6, "R": 1, "M": 12}, "produced_by": None, "claim_ids": [],
        "implementation": "derivado de CoveringLean/A6c_Search.lean `def code12` (inteiros " + str(enc12) + ", bit i = (k // 2^i) % 2)",
        "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

    # estruturas (descrição estruturada de cada código)
    for (cel, m), js in descr_json.items():
        lb = js.get("linear_base") or {}
        gravar("structures", "s-" + wid(cel, m)[2:], {
            "structure_id": "s-" + wid(cel, m)[2:], "kind": "code-structure", "witness": wid(cel, m), "format": js["format"], "group": js.get("group", "Zq"),
            "linear_base_dim": lb.get("k"), "linear_cosets": len(lb.get("coset_syndromes", [])) if lb else 0,
            "subcode_blocks": [{"generators": len(b["generators"]), "reps": len(b["reps"])} for b in js.get("subcode_cosets", [])],
            "patch_words": len(js.get("patch_words", [])), "canonical_sha256": js["canonical_sha256"], "provenance": js["provenance"],
            "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

    # ------------------------------------------------------------------ literatura
    # Fonte: campaigns/covering-codes/_literatura/LITERATURA_CC.md + literatura.csv (revisão adversarial do agente Lit-CC, leitura de 2026-10-03).
    # Cada registro diz o que foi LIDO (texto/tabela/arquivo, uma leitura) e o que foi só RESUMO; nada aqui afirma novidade. A versão e a data
    # de leitura são as que o LITERATURA_CC.md diz ter lido; este script não leu nenhuma fonte, só transcreve o registro da revisão.
    hoje = "2026-10-03"
    LIDO = "LI por Lit-CC em 2026-10-03 (LITERATURA_CC.md; registro transcrito por migrate_covering.py, que não leu a fonte)"
    cel_q = lambda cel: CELULAS[cel]
    ub_claims_de = lambda cel: [f"{cel}-ub-{m}" for cc, m, _ in CODIGOS if cc == cel]

    # --- Marosi, arXiv:2608.19872: 3 versões lidas (texto + tabelas), cada uma com a sua data; o bound_history de K_7(9,4) é 1743 -> 1475 -> 1475
    marosi_t = "New upper and lower bounds on covering codes K_q(n,R) for alphabets of size 5 <= q <= 21"
    MAROSI = [  # (id, versão, data da versão, título, UB de K_7(9,4), trecho)
        ("lit-marosi-2608-19872-v1", "v1", "2026-08-20",
         "título da v1 termina em '...alphabets of size six and seven' (início não transcrito pela revisão); só q em {6,7}", 1743,
         "v1 (2026-08-20): 9 células, só q em {6,7}, sem cotas inferiores; K_7(9,4) <= 1743 no resumo e na tabela; K_7(8,4) <= 329. NÃO tem K_7(8,3)."),
        ("lit-marosi-2608-19872-v2", "v2", "2026-08-23", marosi_t, 1475,
         "v2 (2026-08-23), Tabela 1: linha 'K7 (9,4) 264-1843 | 221 | 1475 | -368 | 20.0% | f | L'; 25 UB + 58 LB; anexo K7_9_4_M1475.txt "
         "(1475 linhas distintas, 9 dígitos, sha256 b3e60549...ac6ace; contei as linhas, NÃO executei)."),
        ("lit-marosi-2608-19872-v3", "v3", "2026-09-02", marosi_t, 1475,
         "v3 (2026-09-02), Tabela 1: K_7(9,4) <= 1475 (igual à v2); 26 UB + 58 LB; declara (Use of artificial intelligence) que manuscrito e software "
         "foram escritos pelo sistema Claude sob direção do autor: fonte a monitorar, não oráculo. Não existe v4 (404 em 2026-10-03)."),
    ]
    for lid, ver, vdata, titulo, ub, trecho in MAROSI:
        L.registrar(c, lid, title=titulo, authors=["Mark Marosi"], year=2026, url=f"https://arxiv.org/abs/2608.19872{ver}", version=ver, version_date=vdata,
                    date_read=hoje, ator=AUTOR, exact_statement=f"{trecho} {LIDO}.", exact_bound="K_7(9,4) <= %d" % ub,
                    bound={"parameters": {"q": 7, "n": 9, "R": 4}, "value": ub, "direction": "upper"},
                    assumptions=["PDF desta versão lido (texto e tabelas) pelo revisor; código e anexos de terceiros NÃO executados"],
                    claim_ids=ub_claims_de("k7-9-4"),
                    open_questions=["a busca local dele para em 1475 e uniões de cosets chegam a 1285 (gap de 190 palavras): por quê? (LITERATURA_CC.md §7.2, HIPÓTESE)"]
                    if ver == "v3" else [])
    for ver, vdata in (("v2", "2026-08-23"), ("v3", "2026-09-02")):  # K_7(8,3): só a cota inferior da Tabela 2 (certificado SDP)
        L.registrar(c, f"lit-marosi-2608-19872-{ver}-k7-8-3-lb", title=marosi_t, authors=["Mark Marosi"], year=2026,
                    url=f"https://arxiv.org/abs/2608.19872{ver}", version=ver, version_date=vdata, date_read=hoje, ator=AUTOR,
                    exact_statement=f"{ver}, Tabela 2: K_7(8,3) >= 471 (certificado SDP). K_7(8,3) não está na Tabela 1 (nenhuma cota superior). {LIDO}.",
                    exact_bound="K_7(8,3) >= 471", bound={"parameters": {"q": 7, "n": 8, "R": 3}, "value": 471, "direction": "lower"},
                    assumptions=["PDF lido pelo revisor"], claim_ids=[])

    # --- Kéri: edição IDENTIFICADA (resolve res-keri-edition-unidentified e res-lb-264-source-unidentified). As tabelas q=2, 4-5, 6-21 são os
    # PDFs de 2009-10-15 (Last-Modified do índice Apache); o index.htm é de 2011-11-25 e a lista de correções vai até 2011-11-21 sem tocar nossas células.
    # Chaves da bibliografia dele (as que a revisão decodificou): m = Haas-Halupczok-Schlage-Puchta 2009; o = Östergård 1999; d = Bhandari-Durairajan 1996;
    # f = soma direta; c = Stanton-Kalbfleisch (1968 e 1969). y e p: significado NÃO transcrito.
    KERI = {  # cel: (arquivo, lb, chave lb, ub, chave ub)
        "k7-9-4": ("6-21_tables.pdf", 264, "m", 1843, "f"), "k7-8-3": ("6-21_tables.pdf", 457, "y", 2337, "f"),
        "k5-7-2": ("4-5_tables.pdf", 225, "m", 525, "o"), "k5-9-3": ("4-5_tables.pdf", 330, "p", 1275, "d"),
        "k5-10-4": ("4-5_tables.pdf", 162, "y", 875, "d"), "k5-9-5": ("4-5_tables.pdf", 19, "m", 55, "d"),
        "k5-9-4": ("4-5_tables.pdf", 64, "m", 255, "d"), "k4-10-4": ("4-5_tables.pdf", 59, "m", 208, "o"),
        "k2-6-1": ("2_tables.pdf", 12, "c", 12, "c"),
    }
    assert {k: v[3] for k, v in KERI.items() if k in KERI_PREVIO} == KERI_PREVIO, "KERI_PREVIO diverge das cotas registradas da revisão"
    for cel, (arq, lbv, lbk, ubv, ubk) in KERI.items():
        q, n, r = cel_q(cel)
        extra = " index.htm (2011-11-25): '875; 720 é provável erro de impressão'." if cel == "k5-10-4" else ""
        for direc, val, chave in (("upper", ubv, ubk), ("lower", lbv, lbk)):
            L.registrar(c, f"lit-keri-{cel}-{'ub' if direc == 'upper' else 'lb'}", title="Tables for bounds on covering codes", authors=["G. Kéri"], year=2009,
                        url="https://old.sztaki.hu/~keri/codes/" + arq,
                        version=f"PDF {arq}, Last-Modified 2009-10-15 (diretório e index.htm atualizados até 2011-11-25)", version_date="2009-10-15",
                        date_read=hoje, ator=AUTOR,
                        exact_statement=f"{arq}: linha K_{q}({n},{r}) = '{lbv}-{ubv}' (chave da cota inferior {lbk}, da superior {ubk}).{extra} {LIDO}, por pdftotext -layout. "
                                        "Três transcrições concordam nesta célula (a do revisor, cov/bounds.json do Marosi e o CSV do Florath).",
                        exact_bound=f"K_{q}({n},{r}) {'<=' if direc == 'upper' else '>='} {val} (chave {chave})",
                        bound={"parameters": {"q": q, "n": n, "R": r}, "value": val, "direction": direc},
                        assumptions=["edição = PDFs de 2009-10-15; 'Kéri 2011' do README/paper = o site atualizado em 2011-11, não tabelas novas",
                                     "a origem de cada chave (artigo/livro) NÃO foi lida"],
                        claim_ids=ub_claims_de(cel) if direc == "upper" else [])

    # --- Gijswijt-Polak, arXiv:2504.01932 v2 (2026-06-19): cotas inferiores citadas (Tab. 3; Tab. 9 para K_5(9,5) e K_5(9,4)). v1 (2025-04-02) NÃO lida.
    gp_t, gp_a = "Semidefinite lower bounds for covering codes", ["D. Gijswijt", "S. Polak"]
    GP = {"k5-7-2": (236, "Tab. 3"), "k4-10-4": (62, "Tab. 3"), "k5-9-3": (354, "Tab. 3"), "k5-10-4": (177, "Tab. 3"),
          "k5-9-5": (15.67, "Tab. 9 (valor real, não arredondado; não melhora o 19 do Kéri)"), "k5-9-4": (61.18, "Tab. 9 (valor real; não melhora o 64 do Kéri)")}
    for cel, (val, tab) in GP.items():
        q, n, r = cel_q(cel)
        L.registrar(c, f"lit-gp-2504-01932v2-{cel}-lb", title=gp_t, authors=gp_a, year=2025, url="https://arxiv.org/abs/2504.01932v2", version="v2",
                    version_date="2026-06-19", date_read=hoje, ator=AUTOR,
                    exact_statement=f"v2, {tab}: K_{q}({n},{r}) >= {val}. {LIDO} (tabelas). A v1 de 2025-04-02 NÃO foi lida.",
                    exact_bound=f"K_{q}({n},{r}) >= {val}", bound={"parameters": {"q": q, "n": n, "R": r}, "value": val, "direction": "lower"},
                    assumptions=["só as tabelas da v2 foram lidas"], claim_ids=[])

    # --- Florath, arXiv:2606.09600 v1 (2026-06-08), repo florath/covering-codes-lean commit bbed9a6 (2026-09-16). O resumo diz 'not new record bounds';
    # K_2(6,1) não aparece no texto. O 10<=K<=12 é o que o LEAN dele prova (non_mixed_covering_codes.csv: '2,6,1,10,12'); a tabela de REFERÊNCIA dele
    # (reference-data/post-keri) tem 12-12, citando Stanton-Kalbfleisch. As duas frases do README são verdadeiras, mas sem esta distinção sugerem que ele não conhece o 12 exato.
    fl_t = "Formal Foundations and Proof-Carrying Certificates for q-ary Covering Codes in Lean 4"
    FL = [("lit-florath-2606-09600-lb", "lower", 10, "Lean dele (reference-data/lean/non_mixed_covering_codes.csv: 2,6,1,10,12): o que ele PROVA no Lean",
           "https://arxiv.org/abs/2606.09600", ["k2-6-1-lb-11"], True),
          ("lit-florath-2606-09600-ub", "upper", 12, "Lean dele (reference-data/lean/non_mixed_covering_codes.csv: 2,6,1,10,12): o que ele PROVA no Lean",
           "https://arxiv.org/abs/2606.09600", ["k2-6-1-ub-12"], True),
          ("lit-florath-postkeri-k2-6-1-lb", "lower", 12, "tabela de REFERÊNCIA dele (reference-data/post-keri: 2,6,1,12,12), citando Stanton-Kalbfleisch",
           "https://github.com/florath/covering-codes-lean", [], False),
          ("lit-florath-postkeri-k2-6-1-ub", "upper", 12, "tabela de REFERÊNCIA dele (reference-data/post-keri: 2,6,1,12,12), citando Stanton-Kalbfleisch",
           "https://github.com/florath/covering-codes-lean", [], False)]
    for lid, direc, val, onde, url, cids, formal in FL:
        L.registrar(c, lid, title=fl_t, authors=["Andreas Florath"], year=2026, url=url, version="v1 (arXiv, 2026-06-08); repositório no commit bbed9a6 (2026-09-16)",
                    version_date="2026-06-08", date_read=hoje, ator=AUTOR,
                    exact_statement=f"K_2(6,1) {'<=' if direc == 'upper' else '>='} {val} na {onde}. Resumo do arXiv: 'not new record bounds'; K_2(6,1) não está no texto do paper. "
                                    f"{LIDO} (resumo, repositório e CSVs; a prova Lean dele NÃO foi compilada).",
                    exact_bound=f"K_2(6,1) {'<=' if direc == 'upper' else '>='} {val}", bound={"parameters": {"q": 2, "n": 6, "R": 1}, "value": val, "direction": direc},
                    formalized=formal, assumptions=["CSVs e README do repositório lidos; prova Lean não compilada"], claim_ids=cids)

    # --- Stanton-Kalbfleisch 1968: SÓ referência citada. O artigo NÃO foi lido. date_read = a data em que a CITAÇÃO foi conferida no Kéri
    # (2_tables.pdf, chave c); a existência do artigo foi conferida antes via Crossref (2026-10-02).
    L.registrar(c, "lit-stanton-kalbfleisch-1968", title="Covering problems for dichotomized matchings", authors=["R. G. Stanton", "J. G. Kalbfleisch"],
                year=1968, url="doi:10.1007/bf01817562", version="Aequationes Math. 1 (1968) 94-103", date_read=hoje, ator=AUTOR, reproduced=False,
                exact_statement="REFERÊNCIA CITADA, não lida: o Kéri (2_tables.pdf, 2009-10-15) atribui K_2(6,1) = 12 à chave c = Stanton-Kalbfleisch (cota inferior: 1968 e 1969), "
                "e a tabela de referência do Florath também. Citação conferida no Kéri em 2026-10-03; existência do artigo (autores, título, volume, páginas) conferida via Crossref "
                "em 2026-10-02. O CONTEÚDO do artigo (que ele determina K_2(6,1)=12) NÃO foi lido.",
                exact_bound="K_2(6,1) = 12", assumptions=["atribuição do valor ao artigo vem do Kéri/Florath, não do artigo"],
                claim_ids=["k2-6-1-eq-12"], open_questions=["conferir no artigo que K_2(6,1)=12 está lá"])

    # ------------------------------------------------------------------ registros formais
    ambiente = F.ambiente(REPO) if not a.sem_lean else {}
    lake_ok = (not a.sem_lean) and F.achar_lake() is not None
    medidos = {  # id -> (teorema, arquivo, módulo)
        **{f"f-sph-{k}": (f"CoveringChain.SPH_{k.upper().replace('-', '_')}_lb", "CoveringLean/Chain.lean", "CoveringLean") for k in LB_ESFERA},
        "f-k2-6-1-ge-11": ("CoveringA6.K_2_6_1_ge_11", "CoveringLean/A6e_Excess.lean", "CoveringLean"),
        "f-sphere-covering": ("CoveringA2.sphere_covering", "CoveringLean/A2_Sphere.lean", "CoveringLean"),
        "f-excess-bound": ("CoveringA6.excess_bound", "CoveringLean/A6e_Excess.lean", "CoveringLean"),
        "f-even-inter": ("CoveringA6.even_inter", "CoveringLean/A6e_Excess.lean", "CoveringLean"),
        "f-code12-covers": ("CoveringA6.code12_covers", "CoveringLean/A6c_Search.lean", "CoveringLean"),
        "f-code12-card": ("CoveringA6.code12_card", "CoveringLean/A6c_Search.lean", "CoveringLean"),
        "f-h2-counterexample": ("CoveringA6.H2_counterexample_uncond", "CoveringLean/A6e_Excess.lean", "CoveringLean"),
        "f-chkn-sound": ("SC.chkN_sound", "CoveringLean/SearchSound.lean", "CoveringLean"),
        "f-cert-of-go": ("CoveringKernel.cert_of_go", "CoveringLean/K3_Bridge.lean", "CoveringLean"),
    }
    for fid, (teo, arq, mod) in medidos.items():
        F.registrar_formal(c, fid, theorem=teo, file=arq, module=mod, raiz_lean=REPO, ator=PROMOTOR, papel="FORMALIZER",
                           rodar_build=lake_ok, lake=None if lake_ok else "/nao/existe/lake")
    pesados = {
        "f-k2-6-1-eq12": ("SC.K_2_6_1_eq12", "CoveringLean/SearchK6ge12.lean", "CoveringLean.SearchK6ge12",
                          sorted(str(p.relative_to(REPO)) for p in (REPO / "CoveringLean").glob("G610_*.lean"))),
        "f-k7-9-4-le-1351": ("CoveringKernel.K7_9_4_le_1351_kernel", "CoveringLean/K3_K7_9_4_Final.lean", "CoveringLean.K3_K7_9_4_Final",
                             sorted(str(p.relative_to(REPO)) for p in (REPO / "CoveringLean").glob("K3_K7_9_4*.lean")) + ["CoveringLean/C1_Data_K7_9_4.lean"]),
    }
    for fid, (teo, arq, mod, fontes) in pesados.items():
        achados = F.escanear_fontes(REPO, [arq, *fontes])
        gravar("formal", fid, {
            "formal_id": fid, "theorem": teo, "module": mod, "file": arq, "lean_root": ".", "lean_version": None,
            "lean_toolchain": ambiente.get("lean_toolchain") or (REPO / "lean-toolchain").read_text().strip(),
            "mathlib_commit": ambiente.get("mathlib_commit"), "manifest_sha256": sha256_arquivo(REPO / "lake-manifest.json"),
            "axioms": None, "declared_axioms": AXIOMAS_DECLARADOS,
            "axioms_status": "DECLARED_NOT_REPRODUCED: README.md:11 e paper/main.tex:156; o módulo é do alvo CoveringHeavy (~12,4 h de CPU), não compilado aqui",
            "sorry_free": not any(x["kind"] in F.TIPOS_SORRY for x in achados), "sorry_free_basis": f"varredura estática de {len(fontes) + 1} fontes (não é build)",
            "clean_build": False, "build_status": "NOT_RUN: lake build CoveringHeavy não executado neste ambiente",
            "repo_commit": commit, "source_sha256": sha256_arquivo(REPO / arq), "scan_findings": achados, "measured": None,
            "validation_problems": ["axiomas não medidos (declarados)", "clean_build não medido"]}, "FORMALIZER", PROMOTOR)

    # ------------------------------------------------------------------ corridas de verificador
    if corridas:
        for cel, m, _ in CODIGOS:
            for vid in ("verify-c", "verify-py-dilation", "verify-rust"):
                V.rodar(c, vid, wid(cel, m), ator=PROMOTOR, papel="INDEPENDENT_VERIFIER", timeout_s=300)
        for vid in ("verify-c", "verify-py-dilation", "verify-rust"):
            V.rodar(c, vid, "w-q2-n6-r1-m12", ator=PROMOTOR, papel="INDEPENDENT_VERIFIER", timeout_s=300)

    # ------------------------------------------------------------------ claims
    def tb(*itens):
        return [{"component": a_, "trusted_for": b_} for a_, b_ in itens]

    TB_LEAN = tb(("kernel do Lean 4 v4.34.1 + Mathlib v4.34.1 (lean-toolchain, lake-manifest.json)", "a correção das inferências e das decisões `decide +kernel`"),
                 ("axiomas propext, Classical.choice, Quot.sound", "lógica clássica e extensionalidade (medido via #print axioms, no alvo padrão)"),
                 ("definições Covers/IsK/ball/hammingDist (CoveringA2, CoveringA6, Mathlib)", "que o enunciado formal é o enunciado pretendido: REVISÃO HUMANA PENDENTE (README:73-74)"))
    TB_C = tb(("tools/verify/verify.c compilado com gcc 13.3 (-Werror)", "que a marcação de bolas e a contagem de descobertos estão certas"),
              ("tools/campaign/verify_cover_dilation.py + numpy 2.4.6", "que a dilatação do grid está certa (2º verificador, independente em código)"),
              ("formato covering-code/v1 (docs/code-format.md)", "convenção de dígitos little-endian e do sha256 canônico"))

    def novo(cid, enunciado, scope, papel="PROPOSER", **extra):
        extra.setdefault("trust_boundary", [])
        K.criar(c, cid, enunciado, ator=AUTOR, papel=papel, scope=scope, **extra)

    def cx(cid, metodo, resultado):
        K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER", counterexample_search={"status": "completed", "method": metodo, "result": resultado})

    def anexa(cid, chave, ref):
        K.anexar_evidencia(c, cid, chave, ref, ator=AUTOR, papel="PROPOSER")

    def promover(cid, para, papel, motivo):
        if para == "PROVED":  # a guarda PROVED do model só exige que exista registro formal; aqui exigimos que ele seja VÁLIDO (medido)
            ruins = [f"{fid}: {x}" for fid in c.ler("claims", cid)["evidence"]["formal"] for x in validar_registro_formal(c.ler("formal", fid))]
            if ruins:
                K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER", blocked_proved=["registro formal inválido/não medido: " + "; ".join(ruins)])
                return ruins
        try:
            K.mudar_estado(c, cid, para, ator=PROMOTOR, papel=papel, motivo=motivo)
            return None
        except TransicaoNegada as e:
            K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER", **{f"blocked_{para.lower()}": e.motivos})
            return e.motivos

    def bloqueios_formal(cid):
        cl = c.ler("claims", cid)
        K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER",
                    formal_verification_blockers=checar_transicao(c, cl, "FORMALLY_VERIFIED", ator=PROMOTOR, papel="FORMALIZER"))

    bound_ = lambda cel, v, d: {"parameters": dict(zip("qnR", CELULAS[cel])), "value": v, "direction": d}

    # lema geral da cota de esfera
    novo("sphere-covering-general",
         "Para todo código C em (ZMod q)^n que cobre com raio R vale q^n <= |C| * V, com V = |bola(R, 0)| (CoveringA2.sphere_covering).",
         {"problem": "cota de esfera", "domain": "Fin n -> ZMod q, hammingDist", "assumptions": ["NeZero q"]}, kind="lemma",
         trust_boundary=TB_LEAN)
    cx("sphere-covering-general", "enunciado geral provado no kernel; contraexemplo impossível sob os axiomas medidos", "nenhum")
    anexa("sphere-covering-general", "formal", "f-sphere-covering")
    promover("sphere-covering-general", "PROVED", "FORMALIZER", "registro formal medido (axiomas, sorry, build) válido")
    bloqueios_formal("sphere-covering-general")

    for cel, lb in LB_ESFERA.items():
        q, n, r = CELULAS[cel]
        cid = f"sph-{cel}-lb"
        novo(cid, f"Todo C : Finset (Fin {n} -> ZMod {q}) com Covers {r} C tem pelo menos {lb} palavras (CoveringChain.SPH_{cel.upper().replace('-', '_')}_lb).",
             {"problem": f"K_{q}({n},{r}) >= {lb}", "domain": f"q={q}, n={n}, R={r}", "assumptions": []}, kind="theorem",
             depends_on=["sphere-covering-general"], bound=bound_(cel, lb, "lower"), trust_boundary=TB_LEAN)
        cx(cid, "cota de esfera: contraexemplo seria um código menor que cobre; o kernel prova que não existe", "nenhum")
        anexa(cid, "formal", f"f-sph-{cel}")
        promover(cid, "PROVED", "FORMALIZER", "registro formal medido válido")
        bloqueios_formal(cid)

    # K_2(6,1)
    novo("excess-bound-lemma", "Para bolas simétricas de tamanho 7 com interseções duas a duas pares, 8*|X| <= 50*|C| se C cobre (CoveringA6.excess_bound).",
         {"problem": "contagem dupla do excesso", "domain": "tipo finito qualquer", "assumptions": ["hcard", "hsymm", "heven"]}, kind="lemma", trust_boundary=TB_LEAN)
    cx("excess-bound-lemma", "lema abstrato provado no kernel", "nenhum")
    anexa("excess-bound-lemma", "formal", "f-excess-bound")
    promover("excess-bound-lemma", "PROVED", "FORMALIZER", "registro formal medido válido")
    novo("even-inter-ball1-binary", "Para a != c em W 2 6, |bola(1,a) ∩ bola(1,c)| é par (CoveringA6.even_inter).",
         {"problem": "paridade da interseção de bolas", "domain": "Fin 6 -> Fin 2", "assumptions": []}, kind="lemma", trust_boundary=TB_LEAN)
    cx("even-inter-ball1-binary", "64 casos decididos no kernel", "nenhum")
    anexa("even-inter-ball1-binary", "formal", "f-even-inter")
    promover("even-inter-ball1-binary", "PROVED", "FORMALIZER", "registro formal medido válido")

    novo("k2-6-1-lb-11", "Todo C : Finset (W 2 6) com Covers 1 C tem pelo menos 11 palavras (CoveringA6.K_2_6_1_ge_11).",
         {"problem": "K_2(6,1) >= 11", "domain": "q=2, n=6, R=1", "assumptions": []}, kind="theorem",
         depends_on=["excess-bound-lemma", "even-inter-ball1-binary"], bound=bound_("k2-6-1", 11, "lower"), trust_boundary=TB_LEAN)
    cx("k2-6-1-lb-11", "contagem dupla sem busca; contraexemplo seria cobertura de 10 palavras, que o kernel exclui", "nenhum")
    anexa("k2-6-1-lb-11", "formal", "f-k2-6-1-ge-11")
    anexa("k2-6-1-lb-11", "literature", "lit-florath-2606-09600-lb")
    promover("k2-6-1-lb-11", "PROVED", "FORMALIZER", "registro formal medido válido")
    bloqueios_formal("k2-6-1-lb-11")

    novo("k2-6-1-ub-12", "Existe C : Finset (W 2 6) com C.card = 12 e Covers 1 C (código `code12`, 12 palavras).",
         {"problem": "K_2(6,1) <= 12", "domain": "q=2, n=6, R=1", "assumptions": []}, kind="theorem", bound=bound_("k2-6-1", 12, "upper"),
         trust_boundary=TB_LEAN, complementary_witnesses=["w-q2-n6-r1-m12"])
    cx("k2-6-1-ub-12", "claim de existência: o certificado é o registro formal (code12_covers + code12_card, medidos no kernel); o witness "
       "w-q2-n6-r1-m12 é redundância computacional FORA de evidence.witnesses (ver complementary_witnesses)", "uncovered=0 nos verificadores; kernel aceita")
    anexa("k2-6-1-ub-12", "formal", "f-code12-covers")
    anexa("k2-6-1-ub-12", "formal", "f-code12-card")
    anexa("k2-6-1-ub-12", "literature", "lit-florath-2606-09600-ub")
    promover("k2-6-1-ub-12", "PROVED", "FORMALIZER", "code12_covers e code12_card medidos no kernel (o PROVED NÃO depende do witness: ele fica em complementary_witnesses, fora de evidence.witnesses)")
    bloqueios_formal("k2-6-1-ub-12")

    novo("chkn-sound-lemma", "SC.chkN n S d s = true -> (fronteira refutada) -> Ref n s (SC.chkN_sound).",
         {"problem": "correção da busca com poda", "domain": "SearchCore", "assumptions": []}, kind="lemma", trust_boundary=TB_LEAN)
    cx("chkn-sound-lemma", "lema provado no kernel", "nenhum")
    anexa("chkn-sound-lemma", "formal", "f-chkn-sound")
    promover("chkn-sound-lemma", "PROVED", "FORMALIZER", "registro formal medido válido")
    novo("k2-6-1-lb-12", "Todo C : Finset (W 2 6) com C.card < 12 não cobre com raio 1 (SC.K_2_6_1_ge12), por busca com poda verificada (chkN_sound) e WLOG 63 ∈ C.",
         {"problem": "K_2(6,1) >= 12", "domain": "q=2, n=6, R=1, espaço finito de 64 palavras", "assumptions": ["translação: WLOG 63 no código"]},
         kind="theorem", depends_on=["chkn-sound-lemma"], bound=bound_("k2-6-1", 12, "lower"), trust_boundary=TB_LEAN + tb(
             ("scripts/k261/sc_ref.py", "espelho Python da MESMA lógica do chkN: só confere o algoritmo, não é verificação independente")))
    cx("k2-6-1-lb-12", "busca exaustiva com controle positivo: `6 10` não acha cobertura de 11, `6 11` acha cobertura de 12", "ver exp-k2-6-1-search-mirror")
    anexa("k2-6-1-lb-12", "experiments", "exp-k2-6-1-search-mirror")
    anexa("k2-6-1-lb-12", "formal", "f-k2-6-1-eq12")
    promover("k2-6-1-lb-12", "EXHAUSTIVE_BOUNDED", "EXHAUSTIVE_SEARCHER", "busca exaustiva (espaço finito) reproduzida em Python; certificado Lean só declarado")
    bloqueios_formal("k2-6-1-lb-12")

    novo("k2-6-1-eq-12", "K_2(6,1) = 12, isto é, IsK 2 6 1 12 (SC.K_2_6_1_eq12).",
         {"problem": "K_2(6,1) = 12", "domain": "q=2, n=6, R=1", "assumptions": [], "parameters": {"q": 2, "n": 6, "R": 1, "M": 12}}, kind="theorem",
         depends_on=["k2-6-1-ub-12", "k2-6-1-lb-12"], covers=["k2-6-1"], trust_boundary=TB_LEAN + TB_C)
    cx("k2-6-1-eq-12", "união das duas metades; ver k2-6-1-ub-12 e k2-6-1-lb-12", "nenhum")
    anexa("k2-6-1-eq-12", "experiments", "exp-k2-6-1-search-mirror")
    anexa("k2-6-1-eq-12", "witnesses", "w-q2-n6-r1-m12")
    anexa("k2-6-1-eq-12", "formal", "f-k2-6-1-eq12")
    anexa("k2-6-1-eq-12", "literature", "lit-stanton-kalbfleisch-1968")
    promover("k2-6-1-eq-12", "EXHAUSTIVE_BOUNDED", "EXHAUSTIVE_SEARCHER", "metade superior provada+reproduzida; metade inferior exaustiva em Python, Lean pesado só declarado")
    bloqueios_formal("k2-6-1-eq-12")

    c.gravar("counterexamples", "cx-h2-gap-nondecreasing", {
        "counterexample_id": "cx-h2-gap-nondecreasing", "claim_id": "h2-gap-nondecreasing", "kind": "instance",
        "description": "gap K - ceil(S) vale 12-10 = 2 em (2,6,1) mas 16-16 = 0 em (2,7,1) (CoveringA6.H2_counterexample_uncond, medido no kernel; "
                       "K_2(6,1)=12 vem dos claims acima, K_2(7,1)=16 de A6b_Hamming.K_2_7_1).",
        "witness_id": None, "data": {"formal": "f-h2-counterexample"}, "created_by": AUTOR, "created": c.meta()["created"]}, ator=AUTOR, papel="COUNTEREXAMPLE_HUNTER")
    novo("h2-gap-nondecreasing", "H2: o gap K_q(n,R) - ceil(esfera) é não decrescente em n (hipótese do autor, A6c_Search.lean:8-12).",
         {"problem": "H2 de A6c_Search", "domain": "q=2, R=1", "assumptions": []}, kind="conjecture")
    anexa("h2-gap-nondecreasing", "formal", "f-h2-counterexample")
    K.mudar_estado(c, "h2-gap-nondecreasing", "CONJECTURE", ator=AUTOR, papel="PROPOSER", motivo="hipótese registrada para ser refutada")
    if not validar_registro_formal(c.ler("formal", "f-h2-counterexample")):  # só refuta se o contraexemplo formal foi MEDIDO
        K.invalidar(c, "h2-gap-nondecreasing", "cx-h2-gap-nondecreasing", ator=PROMOTOR, papel="COUNTEREXAMPLE_HUNTER",
                    motivo="H2_counterexample_uncond medido no kernel")

    # K_7(9,4)
    novo("cert-of-go-lemma", "CoveringKernel.cert_of_go: a checagem booleana `go` verdadeira sobre uma lista estritamente crescente de M inteiros < q^n dá C com |C|=M e Covers R C.",
         {"problem": "ponte checagem -> Covers", "domain": "K3_Bridge", "assumptions": []}, kind="lemma", trust_boundary=TB_LEAN)
    cx("cert-of-go-lemma", "lema provado no kernel", "nenhum")
    anexa("cert-of-go-lemma", "formal", "f-cert-of-go")
    promover("cert-of-go-lemma", "PROVED", "FORMALIZER", "registro formal medido válido")

    for cel, m, no_readme in CODIGOS:
        q, n, r = CELULAS[cel]
        cid = f"{cel}-ub-{m}"
        deps = ["cert-of-go-lemma"] if (cel, m) == ("k7-9-4", 1351) else []
        nota = "" if no_readme else " NÃO consta no README/paper: está em data/codes e docs/code-format.md; novidade não conferida na literatura."
        novo(cid, f"Existe código C em (Z_{q})^{n} com |C| = {m} que cobre com raio {r} (data/codes/{nome_codigo(cel, m)}.txt).{nota}",
             {"problem": f"K_{q}({n},{r}) <= {m}", "domain": f"q={q}, n={n}, R={r}", "assumptions": [], "parameters": {"q": q, "n": n, "R": r, "M": m}},
             kind="theorem", depends_on=deps,
             bound=bound_(cel, m, "upper"), trust_boundary=TB_C + (tb(("Lean kernel (K7_9_4_le_1351_kernel), DECLARADO não reproduzido", "mesmo código, certificado pesado"),
                                                                       ("C1_Data_K7_9_4.lean == witness (medido: exp-lean-data-equals-witness-1351)", "elo entre o teorema e o arquivo"))
                                                                if (cel, m) == ("k7-9-4", 1351) else []) + tb(("literatura registrada (Kéri/Marosi), declarada", "só para a afirmação de que o valor é menor que o anterior, que o Lean não checa")))
        cx(cid, "claim de existência: o witness é o certificado; dois verificadores independentes procuram ponto descoberto (uncovered=0)", "uncovered=0 nos dois verificadores")
        anexa(cid, "witnesses", wid(cel, m))
        anexa(cid, "experiments", {("k7-9-4", 1351): "exp-k7-9-4-1351-lincov", ("k7-9-4", 1285): "exp-k7-9-4-1285-regen"}.get((cel, m), "exp-prior-search-unrecorded"))
        anexa(cid, "literature", f"lit-keri-{cel}-ub")
        if cel == "k7-9-4":
            for v_ in ("v1", "v2", "v3"):
                anexa(cid, "literature", f"lit-marosi-2608-19872-{v_}")
        if (cel, m) == ("k7-9-4", 1351):
            anexa(cid, "experiments", "exp-lean-data-equals-witness-1351")
            anexa(cid, "experiments", "exp-structure-regeneration")
            anexa(cid, "formal", "f-k7-9-4-le-1351")
        if corridas:
            negado = promover(cid, "INDEPENDENTLY_REPRODUCED", "INDEPENDENT_VERIFIER", "2 verificadores de autores/grupos distintos, PASS válido e sem desacordo, neste run")
            if negado:  # a evidência não sustenta IR: o estado honesto é o de baixo (EMPIRICAL: witness + busca de contraexemplo), nunca forçado
                promover(cid, "EMPIRICAL", "PROPOSER", "witness conferido pelo verificador oficial; independência negada pela guarda (ver blocked_independently_reproduced)")
        bloqueios_formal(cid) if c.ler("claims", cid)["evidence"]["formal"] else None

    # ------------------------------------------------------------------ comparação com a literatura REGISTRADA (literature_compare)
    # Registra o veredito em cada claim de cota superior. NÃO afirma novidade: o melhor registrado é o melhor que a revisão LEU, e um predecessor
    # em livro/tabela não lido (res-confirmar-*) invalida qualquer "melhor que".
    CLASSE = {"melhor_que_a_registrada": "MELHORA_APARENTE_A_CONFIRMAR", "igual": "PREDECESSOR_ENCONTRADO",
              "pior_que_a_registrada": "PIOR_QUE_A_REGISTRADA", "SEM_REFERENCIA": "SEM_REFERENCIA"}
    comparacoes = {}
    for cid in [f"{cel}-ub-{m}" for cel, m, _ in CODIGOS] + ["k2-6-1-ub-12"]:
        r_ = L.comparar(c, cid)
        mb = r_.get("melhor_registrada") or {}
        classe = CLASSE[r_["veredito"]]
        nota_ = {"MELHORA_APARENTE_A_CONFIRMAR": "melhora aparente, a confirmar por revisão externa (não é afirmação de novidade: livros/artigos não lidos podem ter predecessor)",
                 "PREDECESSOR_ENCONTRADO": "igual ao valor tabelado: predecessor encontrado na literatura registrada; não há novidade a confirmar"}.get(classe, "")
        comparacoes[cid] = {"veredito": r_["veredito"], "classificacao": classe, "nosso": r_["nosso"], "melhor_registrada": mb.get("value"),
                            "melhor_registrada_fonte": [f"{h['literature_id']} ({h['version']}, {h['version_date']})" for h in r_["historico"] if h["value"] == mb.get("value")], "nota": nota_}
        irmaos_ = sorted(m for cc, m, _ in CODIGOS if cc == cid.rsplit("-ub-", 1)[0])
        if cid.rsplit("-ub-", 1)[0] in CELULAS and len(irmaos_) > 1 and int(cid.rsplit("-ub-", 1)[1]) > irmaos_[0]:
            comparacoes[cid]["nota"] += f"; mas é PIOR que o nosso próprio {irmaos_[0]} da mesma célula"
        K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER", literature_comparison=comparacoes[cid])

    # ------------------------------------------------------------------ resíduos
    def residuo(rid, **campos):
        gravar("residuals", rid, {"residual_id": rid, **campos, "created_by": AUTOR, "created": c.meta()["created"]}, "COORDINATOR")

    def celulas_de(claims_ids):
        """Células (ids do universo) a que os claims se referem, pelo bound.parameters {q,n,R} de cada um (sem bound: nenhuma)."""
        out = set()
        for cid_ in claims_ids:
            b_ = c.ler("claims", cid_).get("bound") if c.tem("claims", cid_) else None
            if b_ and cel_de(b_["parameters"]["q"], b_["parameters"]["n"], b_["parameters"]["R"]):
                out.add(cel_de(b_["parameters"]["q"], b_["parameters"]["n"], b_["parameters"]["R"]))
        return sorted(out)

    for cel, m, no_readme in CODIGOS:
        if cel == "k7-9-4" and m == 1351:
            continue
        residuo(f"res-no-lean-theorem-{cel}-{m}", kind="sem_teorema_lean", claim_id=f"{cel}-ub-{m}", instance=cel, instances=[cel],
                reason="só verificação computacional (verificadores); sem teorema Lean (README:69)",
                next_step="gerar C1_Data_*.lean + folhas K3 (scripts/k794/gen.py) e rodar o alvo pesado, ou provar por síndromes (docs/code-format.md)")
    residuo("res-a6d-searchheavy", kind="fora_da_biblioteca", file="CoveringLean/A6d_SearchHeavy.lean", instances=["k2-6-1"],
            reason="DECLARADO: não compila (README:71, obsoleto com A6e e SearchK6ge12). Não executado aqui (risco de OOM). Célula: K_2(6,1) >= 11 (cabeçalho do arquivo).",
            next_step="apagar (pelo templo: com volta) ou arquivar")
    residuo("res-a5b-stress", kind="fora_da_biblioteca", file="CoveringLean/A5b_Stress.lean", instances=[],
            instances_note="o arquivo trata q=2, n=3, R=1, que não é célula do universo desta campanha",
            reason="DECLARADO: não compila (README:71). MEDIDO: `lake env lean` terminou com rc 137 (SIGKILL) em <=110 s; causa (OOM?) não investigada.",
            next_step="investigar e consertar, ou arquivar")
    heavy_claims = ["k2-6-1-lb-12", "k2-6-1-eq-12", "k7-9-4-ub-1351"]
    residuo("res-heavy-build-not-reproduced", kind="nao_reproduzido", claim_ids=heavy_claims, instances=celulas_de(heavy_claims),
            reason="lake build CoveringHeavy (~12,4 h de CPU, 133 módulos) não foi executado; axiomas desses dois teoremas só DECLARADOS no README/paper",
            next_step="rodar numa máquina com RAM >= 9 GB por módulo e registrar com formal.registrar_formal")
    proved = sorted(cl["claim_id"] for cl in c.listar("claims") if cl["status"] == "PROVED")
    residuo("res-statement-review", kind="revisao_humana", claim_ids=proved, instances=celulas_de(proved),
            reason="FORMALLY_VERIFIED exige statement_review por revisor que não seja o autor; README:73-74 diz que a revisão dos enunciados é humana e pendente",
            next_step="um revisor lê Covers/IsK/ball e os enunciados e registra claim_review(scope='statement')")
    ub_claims = [f"{cel}-ub-{m}" for cel, m, _ in CODIGOS]
    residuo("res-novelty-unchecked", kind="literatura", instances=celulas_de(ub_claims),
            reason="novidade continua sendo afirmação do autor (README:72). Lidos em 2026-10-03 (LITERATURA_CC.md): Marosi v1/v2/v3, Kéri (PDFs de 2009-10-15), Gijswijt-Polak v2 (tabelas), "
            "Florath. NÃO lidos: Cohen et al. 1997, Östergård 1999, Bhandari-Durairajan 1996, Stanton-Kalbfleisch 1968 (conteúdo), tabelas de comprimento linear de "
            "Davydov-Marcugini-Pambianco para l_5(6,4), qualquer trabalho posterior a 2011 fora do arXiv. 'Não achei predecessor' não é 'não existe': ver res-confirmar-* por célula.",
            next_step="ler as fontes listadas em cada res-confirmar-<célula> e reclassificar (MELHORA_APARENTE_A_CONFIRMAR -> PREDECESSOR_ENCONTRADO ou confirmada por revisão externa)")
    # FECHADOS em 2026-10-03 (não são gravados: um resíduo fechado não pode continuar aparecendo em `por_que_restam`):
    #  * res-keri-edition-unidentified: a edição está identificada e registrada (lit-keri-<cel>-ub/-lb, PDFs de 2009-10-15, índice de 2011-11-25, lidos em 2026-10-03);
    #  * res-lb-264-source-unidentified: 264 = Kéri 6-21_tables.pdf, chave m (Haas-Halupczok-Schlage-Puchta 2009), registro lit-keri-k7-9-4-lb.
    # Condição do fechamento, conferida aqui e não assumida: fonte E versão E data de cada cota declarada estão em literature/.
    for cel_, v_ in KERI_PREVIO.items():
        assert c.ler("literature", f"lit-keri-{cel_}-ub")["bound"]["value"] == v_, cel_
    assert c.ler("literature", "lit-keri-k7-9-4-ub")["bound"]["value"] == 1843 and c.ler("literature", "lit-keri-k7-9-4-lb")["bound"]["value"] == 264
    # --- uma pergunta aberta por célula MELHORA_APARENTE_A_CONFIRMAR (LITERATURA_CC.md §2 e §7)
    FALTA = {
        "k7-9-4": ("1285 e 1351 estão abaixo do 1475 do Marosi (v2/v3), mas: (1) Cohen-Honkala-Litsyn-Lobstein 1997 e Östergård 1999 não foram lidos; (2) trabalho de "
                   "Östergård/Rivas Soriano posterior a 2011 e não indexado no arXiv; (3) o 1285 só foi verificado por nós (verify.c, verify_cover_dilation.py, verify-rust); "
                   "rodar o verify_cov.py do Marosi daria independência real, mas é CÓDIGO DE TERCEIROS e NÃO foi executado (precisa de autorização); (4) a busca que produziu "
                   "p1285.json não é reprodutível (sem comando/seed/log)",
                   "autorizar e rodar verify_cov.py sobre data/codes/q7_n9_R4_M1285.txt; ler Cohen et al. 1997 e Östergård 1999; registrar o comando da busca do p1285.json"),
        "k7-8-3": ("1887 e 1893 estão abaixo do 2337 do Kéri (soma direta; Marosi v1-v3 não tem K_7(8,3) na Tabela 1), mas Cohen et al. 1997 e trabalho pós-2011 não foram lidos; "
                   "o 1887 não é reprodutível (172 palavras soltas, sem comando/seed/gerador)",
                   "ler Cohen et al. 1997; registrar como o 1887 foi obtido; rodar verify_cov.py do Marosi se autorizado"),
        "k5-7-2": ("500 < 525 (Kéri, chave o = Östergård 1999): o artigo/livro de Östergård 1999 não foi lido, nem o Cohen et al. 1997", "ler Östergård 1999 e Cohen et al. 1997"),
        "k4-10-4": ("192 < 208 (Kéri, chave o = Östergård 1999): Östergård 1999 e Cohen et al. 1997 não lidos; q=4 está fora do escopo do Marosi e a nossa busca para q=4 é fraca",
                    "ler Östergård 1999 e Cohen et al. 1997; procurar tabelas de q=4 posteriores a 2011"),
        "k5-9-3": ("1250 < 1275 (Kéri, chave d = Bhandari-Durairajan 1996): Bhandari-Durairajan 1996 e Cohen et al. 1997 não lidos", "ler Bhandari-Durairajan 1996 e Cohen et al. 1997"),
        "k5-10-4": ("625 < 875 (Kéri, chave d = Bhandari-Durairajan 1996); é código LINEAR [10,4]_5, o que o torna candidato a predecessor em tabela de comprimento linear que não "
                    "achei: faltou l_5(6,4) em Davydov-Marcugini-Pambianco (0904.3835 v1 e 1808.09301 v2 não têm l_5(6,4)); Bhandari-Durairajan 1996 e Cohen et al. 1997 não lidos",
                    "achar l_5(6,4) (Davydov-Marcugini-Pambianco ou outra tabela de saturating sets/PG(5,5)); ler Bhandari-Durairajan 1996"),
        "k5-9-5": ("50 < 55 (Kéri, chave d = Bhandari-Durairajan 1996): artigo não lido; melhoria de 5 palavras é onde predecessor em tabela mais provavelmente existe (HIPÓTESE)",
                   "ler Bhandari-Durairajan 1996 e Cohen et al. 1997"),
        "k5-9-4": ("250 < 255 (Kéri, chave d = Bhandari-Durairajan 1996): artigo não lido; melhoria de 5 palavras (HIPÓTESE: predecessor provável em tabela)",
                   "ler Bhandari-Durairajan 1996 e Cohen et al. 1997"),
    }
    for cel_, (reason_, next_) in FALTA.items():
        residuo(f"res-confirmar-{cel_}", kind="melhora_aparente_a_confirmar", instances=[cel_], claim_ids=[x for x in ub_claims if x.startswith(cel_ + "-ub-")],
                reason="MELHORA_APARENTE_A_CONFIRMAR (nunca 'novidade'): " + reason_, next_step=next_,
                comparison={x: comparacoes[x] for x in ub_claims if x.startswith(cel_ + "-ub-")})
    bloqueados = [x for x in ub_claims if c.ler("claims", x)["status"] != "INDEPENDENTLY_REPRODUCED"]
    if bloqueados:
        residuo("res-reverify-independent-author", kind="independencia", claim_ids=bloqueados, instances=celulas_de(bloqueados),
                reason="MEDIDO pela guarda de INDEPENDENTLY_REPRODUCED (2026-10-03): verify-c (autor thiagopatzdorf, git log) conta; verify-py-dilation foi escrito por agente-c, "
                       "que também criou os claims, e a guarda não conta verificador do autor do claim. Resta 1 componente independente (< 2), então os 10 claims de "
                       "código ficam em EMPIRICAL (blocked_independently_reproduced traz os motivos exatos). Os dois verificadores continuam concordando; o que falta é um "
                       "segundo AUTOR, não um segundo resultado.",
                next_step="outro agente/humano (diferente de agente-c e de thiagopatzdorf) escreve ou reimplementa um verificador, registra com implemented_by verdadeiro e roda sobre os 11 witnesses")
    residuo("res-1351-generator", kind="geracao_nao_reproduzivel", claim_id="k7-9-4-ub-1351", instances=["k7-9-4"],
            reason="lincov (Mapika/coldcase@56a8cce) fora do repo e remendo guloso de 322 palavras sem registro; gen_lean_cover.py/tests/test_lean_cover.py/data/certificates citados em C1_Data_K7_9_4.lean não existem",
            next_step="registrar o comando do lincov e o algoritmo do remendo, ou versionar o gerador do .lean")
    residuo("res-readme-vs-data", kind="inconsistencia", instances=["k7-9-4", "k7-8-3"],
            reason="data/codes tem M1285 (K_7(9,4)) e M1887 (K_7(8,3)) melhores que os 1351/1893 do paper/main.tex e da nota.md. O README foi corrigido em 2026-10-03 "
                   "(1285/1887 existem e são verificados por 3 verificadores, mas não têm teorema Lean; 'três verificadores independentes' trocado pelo que existe), "
                   "mas paper/main.tex (Zenodo v0.3, publicação: mudança é decisão do dono) ainda diz 'checked by three independent programs' e só cita 1351/1893",
            next_step="o dono decide se publica versão nova do paper; frases a corrigir listadas no relatório do Lit-Integra")

    # ------------------------------------------------------------------ universo (finito) e cobertura
    inst = []
    for cel, (q, n, r) in CELULAS.items():
        melhores = [m for cc, m, _ in CODIGOS if cc == cel]
        inst.append({"id": cel, "q": q, "n": n, "R": r, "lb_formal_esfera": LB_ESFERA.get(cel), "lb_formal_melhor": 12 if cel == "k2-6-1" else LB_ESFERA.get(cel),
                     "ub_verificado_melhor": min(melhores) if melhores else (12 if cel == "k2-6-1" else None), "ub_formal_lean": {"k7-9-4": 1351, "k2-6-1": 12}.get(cel),
                     "size": n})  # o 264 do paper continua fora do universo; a fonte agora é lit-keri-k7-9-4-lb (Kéri, chave m)
    COV.definir_universo(c, {"tipo": "finito", "total": len(inst), "instancias": inst, "estado_minimo_resolvido": "EXHAUSTIVE_BOUNDED",
                             "descricao": "Células (q,n,R) tratadas pela campanha: 8 da cota de esfera (7 com código verificado + K_7(9,4)) e K_2(6,1). "
                                          "'Resolvida' = K_q(n,R) determinado (lb = ub). Só K_2(6,1). As demais têm faixa [lb, ub] aberta."},
                         ator=AUTOR, papel="COORDINATOR")

    # ------------------------------------------------------------------ reproduce.json
    passos = [
        {"id": "ambiente", "type": "ambiente", "requires": ["cc", "python3"], "report_versions": ["cc", "python3"]},
        {"id": "hashes-dos-witnesses", "type": "hashes"},
        {"id": "check-all-verify-c", "type": "dados", "command": ["bash", "tools/verify/check_all.sh"], "timeout_s": 600},
        {"id": "estrutura-regenera", "type": "gerador", "command": ["python3", "scripts/codes/build_structured.py", "--check"], "timeout_s": 600},
        {"id": "gerador-1285", "type": "gerador", "command": ["python3", "-m", "unittest", "tests.test_code_format.GeneratorsRegenerateTheCodes", "-v"], "timeout_s": 600},
        {"id": "espelho-busca-k2-6-1", "type": "gerador", "command": ["python3", "scripts/k261/sc_ref.py", "6", "10", "2"], "timeout_s": 120},
        {"id": "testes-unittest", "type": "teste", "command": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], "timeout_s": 900},
        {"id": "verificadores-sobre-witnesses", "type": "verificadores"},
        {"id": "lake-build-alvo-padrao", "type": "lean_build", "lean_root": ".", "target": None, "opcional": True,
         "nota": "alvo padrão CoveringLean (8942 jobs); CoveringHeavy (~12,4 h de CPU) NÃO está aqui"},
        {"id": "axiomas-dos-registros-formais", "type": "axiomas"},
        {"id": "auditoria-da-cadeia", "type": "auditoria"},
    ]
    (raiz / "reproduce.json").write_text(json.dumps({"schema": "genesis-math/reproduce/v1", "campaign_id": CAMPANHA, "steps": passos},
                                                    ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ âncora da cabeça da cadeia (Campanha.ancorar = campaign_anchor)
    # Sem GENESIS_MATH_ANCHOR_KEY no ambiente o HMAC fica null (nenhum segredo é inventado aqui). audit/anchors.jsonl é versionável: o commit
    # no remoto git é a cópia fora do disco; GENESIS_MATH_ANCHOR_EXTERNAL, se definida, recebe a mesma linha.
    ancora = ancorar_campanha(c, PROMOTOR)

    # ------------------------------------------------------------------ resumo
    res = K.resumo_por_estado(c)
    print(json.dumps({"estados": {k: v for k, v in res.items() if v}, "cadeia_de_auditoria": c.verificar_cadeia(), "ancora": {k: ancora.get(k) for k in ("seq", "hash", "hmac", "copia_externa", "aviso")},
                      "cobertura": {k: v for k, v in COV.coverage(c).items() if k in ("total", "resolved", "residual", "refuted")}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
