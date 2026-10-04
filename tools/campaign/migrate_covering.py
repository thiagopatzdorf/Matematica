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
    `scope.parameters` (M = `bound.value`); os verificadores recebem os parâmetros por `{param:NOME}` e NÃO leem o nome do arquivo; cada
    verificador registra o autor REAL (`implemented_by`: git log ou a declaração do README da ferramenta). Verificador do autor do claim
    (verify-py-dilation) e verificadores do mesmo autor de outro (verification/*, mesmo autor de verify.c) não contam como componentes extras;
  * v0.5 (merge do main, 2026-10-03): a campanha foi refeita sobre os 12 códigos de data/codes e sobre os teoremas Lean que EXISTEM:
      - `Syn.K7_9_4_le_{1137,1141,1285,1351}_syn` e `Syn.K7_8_3_le_1887_syn` (lib CoveringSyn): axiomas MEDIDOS aqui por `#print axioms` real;
        o claim de cada um sobe a PROVED só se o registro formal é válido (sem sorry, build limpo, axiomas esperados) E há ≥2 componentes
        independentes de verificador (a guarda de PROVED exige as duas coisas quando o claim tem witness);
      - `CoveringKernel.K*_kernel` e `SC.K_2_6_1_eq12` (lib CoveringHeavy, ~9,3 h de CPU): NÃO compilados aqui; o registro formal guarda os
        axiomas declarados em `declared_axioms`, com `axioms: null`, e NÃO sustenta promoção. Desde 2026-10-04 existe uma medição EXTERNA
        (VM do autor, `_fatos/medicao_heavy_vm.json`): entra em `measured_external` e em `axioms_status = MEASURED_ON_EXTERNAL_VM`, mas
        `axioms`/`clean_build` continuam os que a campanha mediu (nada), então a guarda segue negando PROVED. Desde 2026-10-04 ela TAMBÉM é
        registrada como `kernel_runs/kr-heavy-ddb16b7-lean-build2` (eixo do kernel, `factory_cauteloso.matematica.kernel`): nível
        EXTERNAL_RUN_REPORTED (o log bruto não foi persistido: só o prefixo do sha256), nenhum claim muda de estado, e o nível nunca é gravado
        (é calculado pela infraestrutura). Não é reprodução independente: foi uma execução do próprio autor;
  * FORMALLY_VERIFIED nunca é pedido de fato: exige `statement_review` de um revisor que não seja o autor e ninguém revisou os
    enunciados (README: "revisão humana"). Os motivos exatos da guarda ficam em `formal_verification_blockers` de cada claim.
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
# códigos de data/codes (12 no main v0.5): (célula, M). O 3º elemento de CODIGOS (o código aparece no README ou no paper?) é MEDIDO nos textos, não escrito.
_BASE_CODIGOS = [("k5-7-2", 500), ("k4-10-4", 192), ("k5-9-3", 1250), ("k5-10-4", 625), ("k5-9-5", 50), ("k5-9-4", 250), ("k7-8-3", 1893), ("k7-8-3", 1887),
                 ("k7-9-4", 1351), ("k7-9-4", 1285), ("k7-9-4", 1141), ("k7-9-4", 1137)]
_TEXTO_PUBLICO = (REPO / "README.md").read_text(encoding="utf-8") + (REPO / "paper" / "main.tex").read_text(encoding="utf-8")
CODIGOS = [(cel, m, re.search(rf"(?<![\d.]){m}(?![\d])", _TEXTO_PUBLICO) is not None) for cel, m in _BASE_CODIGOS]
# Teoremas Lean por síndromes (lib CoveringSyn, módulo CoveringLean.Syn_K<M>): existem no main v0.5 e são MEDIDOS aqui. cel/M -> nome do teorema.
SYN = {("k7-9-4", 1137): "Syn.K7_9_4_le_1137_syn", ("k7-9-4", 1141): "Syn.K7_9_4_le_1141_syn", ("k7-9-4", 1285): "Syn.K7_9_4_le_1285_syn",
       ("k7-9-4", 1351): "Syn.K7_9_4_le_1351_syn", ("k7-8-3", 1887): "Syn.K7_8_3_le_1887_syn"}
# Teoremas Lean por prefixos (lib CoveringHeavy, ~9,3 h de CPU): DECLARADOS, não compilados aqui. cel/M -> (teorema, arquivo Final).
HEAVY = {("k7-9-4", 1351): ("CoveringKernel.K7_9_4_le_1351_kernel", "CoveringLean/K3_K7_9_4_Final.lean", "K7_9_4"),
         ("k7-8-3", 1893): ("CoveringKernel.K7_8_3_le_1893_kernel", "CoveringLean/K3_K7_8_3_Final.lean", "K7_8_3"),
         ("k5-7-2", 500): ("CoveringKernel.K5_7_2_le_500_kernel", "CoveringLean/K3_K5_7_2_Final.lean", "K5_7_2"),
         ("k4-10-4", 192): ("CoveringKernel.K4_10_4_le_192_kernel", "CoveringLean/K3_K4_10_4_Final.lean", "K4_10_4"),
         ("k5-9-3", 1250): ("CoveringKernel.K5_9_3_le_1250_kernel", "CoveringLean/K3_K5_9_3_Final.lean", "K5_9_3"),
         ("k5-10-4", 625): ("CoveringKernel.K5_10_4_le_625_kernel", "CoveringLean/K3_K5_10_4_Final.lean", "K5_10_4"),
         ("k5-9-5", 50): ("CoveringKernel.K5_9_5_le_50_kernel", "CoveringLean/K3_K5_9_5_Final.lean", "K5_9_5"),
         ("k5-9-4", 250): ("CoveringKernel.K5_9_4_le_250_kernel", "CoveringLean/K3_K5_9_4_Final.lean", "K5_9_4")}


def fid_heavy(tag: str, m: int) -> str:
    return f"f-heavy-{tag.lower().replace('_', '-')}-{m}"


TRACER_BUCKET = "gs://factory-cauteloso-telemetria/matematica/kernel-runs"  # onde os logs do traçador foram enviados (nome = sha256 do log)
KR_HEAVY = "kr-heavy-ddb16b7-lean-build2"  # a execução externa histórica do CoveringHeavy (kernel_runs/); o log bruto NÃO foi persistido
CUSTO_HEAVY = "~9,3 h de CPU (README.md: `lake build CoveringHeavy` 1 h 54 min de relógio, pico 9,4 GB por processo)"
KERI_PREVIO = {"k5-7-2": 525, "k4-10-4": 208, "k5-9-3": 1275, "k5-10-4": 875, "k5-9-5": 55, "k5-9-4": 255, "k7-8-3": 2337}
AXIOMAS_DECLARADOS = ["propext", "Classical.choice", "Quot.sound"]
# Autor do verify_cover_dilation.py: o agente que o escreveu NESTA campanha (primeira sessão, commit 483a6c5 assinado "Claude"; na campanha esse agente
# é `agente-c`, o mesmo que cria os claims). Registrar outro nome seria inventar autor; a guarda de independência reprova e isso é um achado.
AUTOR_DILATACAO = AUTOR
# Autor do verify-rust: o agente "Verif-Rust" desta sessão, que recebeu só a especificação do problema e docs/code-format.md (não leu verify.c nem o
# verificador em Python): independência de autoria e de lógica declarada em tools/verify-rust/README.md.
AUTOR_RUST = "agente-verif-rust"
# Autor do clean-room (tools/verify-cleanroom, Go): README da ferramenta declara um agente distinto que NÃO leu verify.c, a dilatação nem o Rust. O git log só
# diz "Claude" (assinatura do motor), então o nome do README é o único registro de autoria distinta; fica declarado como tal nas notas.
AUTOR_CLEANROOM = "agente-verif-cleanroom"
# Registrar também os A/B/C de verification/ (main v0.5)? Eles são do mesmo autor de verify.c: não somam independência e fazem o lint `same_code_verifier` (alta) acusar
# "7 verificadores PASS contam como 4" nos claims de K_7(9,4). Isso é verdade, não defeito, mas é um vermelho que não some. Mude para False para só documentá-los.
REGISTRAR_VERIFICATION_DO_MAIN = True
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
    from factory_cauteloso.matematica import claims as K, coverage as COV, formal as F, kernel as KR, literature as L, verify as V  # noqa: E402
    from factory_cauteloso.matematica.model import TransicaoNegada, checar_transicao, validar_registro_formal  # noqa: E402
    from factory_cauteloso.matematica.store import Campanha, sha256_arquivo  # noqa: E402

    raiz = REPO / "campaigns" / CAMPANHA
    if a.so_ancorar:
        print(json.dumps(ancorar_campanha(Campanha(raiz), PROMOTOR), ensure_ascii=False, indent=1))
        return 0
    # ------------------------------------------------------------------ zera só o que o armazenamento criou
    for nome in ("campaign.json", "audit", "reproduce.json", "reports", "artifacts", "claims", "experiments", "witnesses", "counterexamples",
                 "structures", "reductions", "transfer", "families", "residuals", "formal", "verifiers", "verifier_runs", "literature",
                 "reports", "provenance", "kernel_runs"):
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
    raiz_fatos = raiz / "_fatos"

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
    # 4º verificador (2026-10-03): clean-room em Go (BFS multi-fonte), escrito por outro agente; README declara o que foi lido.
    V.registrar_verificador(c, "verify-cleanroom", language="go", source_files=["tools/verify-cleanroom/main.go", "tools/verify-cleanroom/go.mod"],
                            independence_group="go-bfs-multisource", fail_exit_codes=[1, 2], timeout_s=300, ator=AUTOR, papel="PROPOSER",
                            implemented_by=AUTOR_CLEANROOM, command=["{workdir}/verify-cleanroom", *PARAMS_CMD, "{witness}"],
                            build=[["go", "build", "-C", "tools/verify-cleanroom", "-o", "{workdir}/verify-cleanroom", "."]])
    # Os três verificadores que o main v0.5 trouxe (verification/, validação de K_7(9,4) <= 1137). Medido no git log: UM commit, UM autor (o mesmo de
    # tools/verify/verify.c). Por isso `implemented_by` é esse autor e a guarda os junta com verify-c no mesmo componente (não somam independência).
    # Têm q=7, n=9 (e R=4 em B e C) cravados no código: só se aplicam às instâncias K_7(9,4); `applies_to` registra isso e as corridas só rodam nelas.
    autor_val = autor_do_arquivo("verification/verify_bruteforce.c")
    VAL_IDS = ("verify-val-bruteforce", "verify-val-balls", "verify-val-bfs")
    assert autor_val == autor_do_arquivo("verification/verify_balls.py") == autor_do_arquivo("verification/verify_bfs/main.rs"), "autores diferem: rever implemented_by"
    APLICA_794 = {"q": 7, "n": 9, "R": 4}
    if REGISTRAR_VERIFICATION_DO_MAIN:
        V.registrar_verificador(c, "verify-val-bruteforce", language="c", source_files=["verification/verify_bruteforce.c"], independence_group="c-openmp-bruteforce-verification",
                                fail_exit_codes=[1], timeout_s=900, ator=AUTOR, papel="PROPOSER", implemented_by=autor_val,
                                command=["{workdir}/verify_bruteforce", "{witness}", "{param:M}", "{param:R}"],
                                build=[["cc", "-O2", "-fopenmp", "-o", "{workdir}/verify_bruteforce", "verification/verify_bruteforce.c"]])
        V.registrar_verificador(c, "verify-val-balls", language="python", source_files=["verification/verify_balls.py"], independence_group="python-numpy-balls-verification",
                                fail_exit_codes=[1], timeout_s=900, ator=AUTOR, papel="PROPOSER", implemented_by=autor_val,
                                command=["python3", "verification/verify_balls.py", "{witness}", "{param:M}"])
        V.registrar_verificador(c, "verify-val-bfs", language="rust", source_files=["verification/verify_bfs/main.rs"], independence_group="rust-bfs-verification",
                                fail_exit_codes=[1], timeout_s=900, ator=AUTOR, papel="PROPOSER", implemented_by=autor_val,
                                command=["{workdir}/verify_bfs", "{witness}", "{param:M}"],
                                build=[["rustc", "-O", "-o", "{workdir}/verify_bfs", "verification/verify_bfs/main.rs"]])
    contrato = (f" Contrato de saída: 0 cobre, 1 ponto descoberto, 2 o witness contradiz os parâmetros (FAIL = fail_exit_codes [1, 2]); 3 uso/falha operacional "
                f"(ERROR, nunca FAIL). Recebe q,n,R,M por {{param:NOME}} e rejeita nome de arquivo que diga outra instância. Modificado em 2026-10-03 por "
                f"{MODIFICADO_POR} (parâmetros explícitos); o autor original (implemented_by) segue o do git log.")
    def nota_val(parametros):
        return (" Veio no main v0.5 (verification/, VALIDATION.md). git log: um commit (\"validate(k794): validação independente de K_7(9,4) ≤ 1137 (#10)\"), autor "
                f"{autor_val}, o MESMO de tools/verify/verify.c: a guarda de independência os junta com verify-c num componente só. VALIDATION.md diz que A, B e C têm "
                "parser e noção de cobertura próprios e nenhum código compartilhado (independência de método, não de autoria). q=7 e n=9 estão cravados no código "
                f"(aplica-se só a K_7(9,4)); recebe {parametros} por {{param:NOME}}; as corridas só rodam nos witnesses de K_7(9,4). Um witness de outra instância seria "
                "recusado no parser (comprimento/dígitos), nunca aceito em silêncio.")

    notas_v = {
        "verify-cleanroom": ("Escrito por outro agente (declarado no README da ferramenta) que NÃO leu verify.c, verify_cover_dilation.py nem tools/verify-rust; BFS multi-fonte "
                             "no grafo de Hamming H(n,q), O(q^n·n·q). O git log só assina 'Claude' (motor), então a autoria distinta é a DECLARADA no README, não verificável "
                             "pelo git. Independente em linguagem, código e algoritmo; NÃO em especificação do problema." + contrato),
        "verify-rust": ("Escrito por outro agente (agente-verif-rust) sem ler os outros dois verificadores nem o gerador do formato; algoritmo de dilatação "
                        "por camadas com um byte por ponto (OR ao longo de cada reta de coordenada), O(R·n·q^n). Declaração de independência e do que foi lido em "
                        "tools/verify-rust/README.md. Independente em linguagem, código, algoritmo e autoria; NÃO em especificação do problema (a definição de código de cobertura é a mesma)."),
        "verify-c": (f"Verificador oficial do repositório (marca bolas de raio R num bitset). Escrito antes desta campanha por {autor_c} "
                     f"(autor do primeiro commit de tools/verify/verify.c)." + contrato),
        "verify-py-dilation": ("Escrito NESTA campanha pelo mesmo agente que cria os claims (agente-c): independente em linguagem, código e algoritmo "
                               "(dilatação do indicador do código no grid, sem enumerar bolas), mas NÃO em autoria nem em especificação do formato. "
                               "Concorda com verify-c em positivos e negativos (tests/test_campaign_verifier.py). Por ter o mesmo autor dos claims, a guarda de "
                               "INDEPENDENTLY_REPRODUCED não conta este verificador (achado, não defeito)." + contrato),
        "verify-val-bruteforce": "Verificador A de VALIDATION.md: para todo x calcula d(x,C) = min sobre as palavras (força bruta, C + OpenMP)." + nota_val("M e R"),
        "verify-val-balls": "Verificador B de VALIDATION.md: marca a bola de raio r de cada palavra (vetores de erro por itertools, NumPy); R=4 cravado." + nota_val("M"),
        "verify-val-bfs": "Verificador C de VALIDATION.md: BFS multi-fonte no grafo H(9,7) (Rust); R=4 cravado." + nota_val("M"),
    }
    for vid, nota in notas_v.items():
        if vid in VAL_IDS and not REGISTRAR_VERIFICATION_DO_MAIN:
            continue
        r = c.ler("verifiers", vid)
        r["notes"] = nota
        if vid.startswith("verify-val-"):
            r["applies_to"] = dict(APLICA_794)
        c.gravar("verifiers", vid, r, ator=AUTOR, papel="PROPOSER", acao="verifiers.note")

    def aplica(vid, cel):
        """O verificador se aplica à instância? (os de `applies_to` só rodam nas instâncias que declaram)"""
        if not c.tem("verifiers", vid):
            return False
        ap_ = c.ler("verifiers", vid).get("applies_to")
        return ap_ is None or dict(zip("qnR", CELULAS[cel])) == ap_

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

    def regen_de(m):
        """Regenera o código de K_7(9,4) com M palavras por scripts/search/gen.py a partir de data/search/p<M>.json e compara com o witness."""
        r_ = {"executado_neste_run": False}
        if corridas:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / f"q7_n9_R4_M{m}.txt"
                r = exec_(["python3", "scripts/search/gen.py", f"data/search/p{m}.json", str(out)])
                wit = REPO / f"data/codes/q7_n9_R4_M{m}.txt"
                r_ = {"executado_neste_run": True, "rc": r["rc"], "stdout": r["stdout"].strip(),
                      "sha256_regenerado": sha_bytes(out) if out.is_file() else None, "sha256_witness": sha_bytes(wit),
                      "identico_byte_a_byte": out.is_file() and out.read_bytes() == wit.read_bytes(),
                      "sha256_canonico_regenerado": canonico(out) if out.is_file() else None, "sha256_canonico_witness": canonico(wit),
                      "mesmo_conjunto_de_palavras": out.is_file() and canonico(out) == canonico(wit)}
        return r_

    for m_ in (1285, 1137):
        gravar("experiments", f"exp-k7-9-4-{m_}-regen", {
            "experiment_id": f"exp-k7-9-4-{m_}-regen", "kind": "search",
            "description": f"Regenera o código de {m_} palavras com o gerador versionado a partir de data/search/p{m_}.json e compara com o witness: byte a byte "
                           "(identico_byte_a_byte) e como CONJUNTO de palavras (sha256 canônico; a ordem das linhas pode diferir). Isto reproduz a ESTRUTURA do código, "
                           "não a busca que achou os parâmetros p<M>.json.",
            "ranges": None, "implementation": "scripts/search/gen.py",
            "command": ["python3", "scripts/search/gen.py", f"data/search/p{m_}.json", "<saída>"],
            "source_files": [{"path": p_, "sha256": sha256_arquivo(REPO / p_)} for p_ in ("scripts/search/gen.py", f"data/search/p{m_}.json")],
            "instances": ["k7-9-4"], "result": regen_de(m_), "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

    gravar("experiments", "exp-k7-9-4-1141-kit", {
        "experiment_id": "exp-k7-9-4-1141-kit", "kind": "search",
        "description": "Busca que produziu o código de 1141 palavras: enumeração exata das 6362 classes de [9,3]_7 + otimizador de remendo (112 palavras), no 'kit de busca' "
                       "(branch feat/kit-de-busca, VM lean-build2). DECLARADO em data/structured/q7_n9_R4_M1141.json; NÃO reproduzível aqui: o kit não está neste repositório, "
                       "não há data/search/p1141.json e nenhum comando/seed foi registrado. O que é reproduzível é a estrutura (build_structured --check) e a verificação.",
        "ranges": None, "implementation": "kit de busca (feat/kit-de-busca), fora deste repositório", "command": None, "source_files": [],
        "instances": ["k7-9-4"], "result": {"reproduzivel_aqui": False, "executado_neste_run": False, "declarado_em": "data/structured/q7_n9_R4_M1141.json; README.md (v0.5)"},
        "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "EXHAUSTIVE_SEARCHER")

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

    # elo Lean (síndromes) <-> witness (calculado, não declarado): decodifica a lista LK<M> E o campo empacotado PN (o que o teorema de fato usa:
    # `unpack b cnt PN = L`) de CoveringLean/SynData_K<M>.lean e compara o sha256 canônico com o do witness.
    sys.set_int_max_str_digits(0)
    for (cel_s, m_s), teo_s in SYN.items():
        q_, n_, r_ = CELULAS[cel_s]
        arq_s = f"CoveringLean/SynData_K{m_s}.lean"
        txt_s = (REPO / arq_s).read_text()
        lista = [int(x) for x in re.search(rf"def LK{m_s} : List Nat := \[([^\]]*)\]", txt_s).group(1).split(",")]
        campo = lambda nome: int(re.search(rf"^\s*{nome} := (\d+)\s*$", txt_s, re.M).group(1))  # noqa: E731
        b_s, cnt_s, pn_s = campo("b"), campo("cnt"), campo("PN")
        desemp = [(pn_s >> (b_s * j)) & ((1 << b_s) - 1) for j in range(cnt_s)]
        sha_s = hashlib.sha256(("\n".join(sorted("".join(str((w // q_ ** k) % q_) for k in range(n_)) for w in lista)) + "\n").encode()).hexdigest()
        sha_wit = canonico(REPO / "data/codes" / f"{nome_codigo(cel_s, m_s)}.txt")
        gravar("experiments", f"exp-lean-syn-data-equals-witness-{m_s}", {
            "experiment_id": f"exp-lean-syn-data-equals-witness-{m_s}", "kind": "symbolic",
            "description": f"Decodifica a lista LK{m_s} (e o campo empacotado PN) de {arq_s} (base {q_} little-endian) e compara o sha256 canônico com o de "
                           f"data/codes/{nome_codigo(cel_s, m_s)}.txt: o elo entre o teorema {teo_s} e o arquivo verificado por programas.",
            "ranges": None, "implementation": "regex + sha256 em tools/campaign/migrate_covering.py (independente de scripts/syndrome/check_sha.py)",
            "source_files": [{"path": arq_s, "sha256": sha256_arquivo(REPO / arq_s)}], "instances": [cel_s],
            "result": {"palavras": len(lista), "cnt_declarado": cnt_s, "estritamente_crescente": lista == sorted(set(lista)), "todas_menores_que_q_n": max(lista) < q_ ** n_,
                       "unpack_PN_igual_a_lista": desemp == lista, "sha256_canonico_lean": sha_s, "sha256_canonico_witness": sha_wit, "iguais": sha_s == sha_wit,
                       "executado_neste_run": True},
            "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

    # ------------------------------------------------------------------ witnesses
    PRODUZIDO_POR = {("k7-9-4", 1351): "exp-k7-9-4-1351-lincov", ("k7-9-4", 1285): "exp-k7-9-4-1285-regen", ("k7-9-4", 1141): "exp-k7-9-4-1141-kit",
                     ("k7-9-4", 1137): "exp-k7-9-4-1137-regen"}
    descr_json = {}
    for cel, m, _ in CODIGOS:
        nome = nome_codigo(cel, m)
        p = REPO / "data/codes" / f"{nome}.txt"
        js = json.loads((REPO / "data/structured" / f"{nome}.json").read_text())
        produzido = PRODUZIDO_POR.get((cel, m), "exp-prior-search-unrecorded")
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

    # --- STATE_OF_ART.md (main v0.5, revisão de 2026-10-02 sobre K_7(9,4)): NÃO é fonte primária. Cada afirmação dele é conferida contra os registros acima
    # (que vêm das fontes lidas em 2026-10-03) e o que não tem registro fica "SEM_REGISTRO": o texto não vira evidência por existir.
    soa = (REPO / "STATE_OF_ART.md").read_text(encoding="utf-8")
    lit_ = lambda i: c.ler("literature", i)  # noqa: E731
    itens_soa = []

    def item_soa(afirmacao, padrao, registro, esperado):
        achou = re.search(padrao, soa, re.S) is not None
        itens_soa.append({"afirmacao": afirmacao, "presente_no_STATE_OF_ART": achou, "registro_da_campanha": registro, "esperado_pelo_STATE_OF_ART": esperado,
                          "confere": (registro == esperado) if registro is not None else None,
                          "veredito": ("SEM_REGISTRO (não confirmado por esta campanha)" if registro is None else ("CONFERE" if registro == esperado else "DIVERGE")) if achou else "NÃO_ENCONTRADA_NO_TEXTO"})
    item_soa("menor UB publicado = 1475 (Marosi v2)", r"K_7\(9,4\) <= 1475", lit_("lit-marosi-2608-19872-v2")["bound"]["value"], 1475)
    item_soa("menor UB publicado = 1475 (Marosi v3, versão atual)", r"v3\*\* \(atual\).{0,200}?\*\*1475\*\*", lit_("lit-marosi-2608-19872-v3")["bound"]["value"], 1475)
    item_soa("v1 do Marosi = 1743", r"\*\*v1\*\*.{0,300}?\*\*1743\*\*", lit_("lit-marosi-2608-19872-v1")["bound"]["value"], 1743)
    item_soa("v1 de 2026-08-20", r"2026-08-20", lit_("lit-marosi-2608-19872-v1")["version_date"], "2026-08-20")
    item_soa("v2 de 2026-08-23", r"2026-08-23", lit_("lit-marosi-2608-19872-v2")["version_date"], "2026-08-23")
    item_soa("v3 de 2026-09-02", r"2026-09-02", lit_("lit-marosi-2608-19872-v3")["version_date"], "2026-09-02")
    item_soa("Kéri: UB 1843 (soma direta)", r"\*\*1843\*\* \(chave `f`", lit_("lit-keri-k7-9-4-ub")["bound"]["value"], 1843)
    item_soa("cota inferior 264 (Haas-Halupczok-Schlage-Puchta 2009, chave m do Kéri)", r"264 \(`m`\)", lit_("lit-keri-k7-9-4-lb")["bound"]["value"], 264)
    item_soa("Kéri: PDF de 2009-10-15", r"arquivo de 2009-10-15", lit_("lit-keri-k7-9-4-ub")["version_date"], "2009-10-15")
    item_soa("cota de esfera = 221", r"sphere 221", LB_ESFERA["k7-9-4"], 221)
    item_soa("Δ = 1843 - 1475 = 368 (-368 na Tabela 1 do Marosi)", r"−368", lit_("lit-keri-k7-9-4-ub")["bound"]["value"] - lit_("lit-marosi-2608-19872-v2")["bound"]["value"], 368)
    item_soa("368/1843 arredondado a 20.0%", r"20\.0%", round(100 * 368 / 1843, 1), 20.0)
    item_soa("sha256 do anexo M1475 começa em b3e60549 e termina em ac6ace (Marosi v2/v3)", r"b3e60549…ac6ace",
             all("b3e60549...ac6ace" in lit_(x)["exact_statement"] for x in ("lit-marosi-2608-19872-v2",)), True)
    item_soa("v4 do Marosi não existe (404)", r"v4 não existe", "Não existe v4" in lit_("lit-marosi-2608-19872-v3")["exact_statement"], True)
    item_soa("nenhum resultado registrado abaixo de 1475 para K_7(9,4)", r"Não achei nenhum resultado com K_7\(9,4\) <= N para N <= 1137",
             min(h["bound"]["value"] for h in c.listar("literature") if h.get("bound") and h["bound"]["parameters"] == {"q": 7, "n": 9, "R": 4} and h["bound"]["direction"] == "upper"), 1475)
    item_soa("Gijswijt-Polak cobrem só q <= 5 (não citam K_7(9,4))", r"só cobrem q = 2, 3, 4, 5",
             all(h["bound"]["parameters"]["q"] <= 5 for h in c.listar("literature") if h["literature_id"].startswith("lit-gp-")), True)
    item_soa("Florath (repositório): K_7(9,4) <= 2401 por lengthenFreeN", r"upper 2401", None, 2401)
    item_soa("Mapika/coldcase: arquivos de K7(9,4) de 1475 a 1843, commit 56a8cce", r"HEAD do master `56a8cce`", None, "56a8cce")
    item_soa("o código M1475 do Marosi cobre os 7^9 pontos (reverificado pelo autor do STATE_OF_ART com numpy)", r"zero descobertas", None, True)
    soa_resumo = {"confere": sum(i["veredito"] == "CONFERE" for i in itens_soa), "diverge": sum(i["veredito"] == "DIVERGE" for i in itens_soa),
                  "sem_registro": sum(i["veredito"].startswith("SEM_REGISTRO") for i in itens_soa), "nao_encontrada": sum(i["veredito"] == "NÃO_ENCONTRADA_NO_TEXTO" for i in itens_soa)}
    gravar("experiments", "exp-state-of-art-crosscheck", {
        "experiment_id": "exp-state-of-art-crosscheck", "kind": "symbolic",
        "description": "Confere STATE_OF_ART.md (main v0.5, revisão de 2026-10-02) contra os registros de literatura desta campanha (fontes lidas por Lit-CC em 2026-10-03). O documento NÃO é fonte "
                       "primária e não vira evidência por existir; afirmação sem registro correspondente fica SEM_REGISTRO. Não afirma novidade: STATE_OF_ART.md, VALIDATION.md e o paper dizem 'o menor "
                       "que encontramos nas fontes revisadas', e o próprio documento lista o que não checou (Google Scholar, bases pagas, teses, periódico, páginas pessoais).",
        "ranges": None, "implementation": "regex + comparação com literature/ em tools/campaign/migrate_covering.py",
        "source_files": [{"path": "STATE_OF_ART.md", "sha256": sha256_arquivo(REPO / "STATE_OF_ART.md")}], "instances": ["k7-9-4"],
        "result": {"itens": itens_soa, "resumo": soa_resumo, "executado_neste_run": True}, "repo_commit": commit, "created_by": AUTOR, "created": c.meta()["created"]}, "STRUCTURAL_ANALYST")

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
        # H1, H3, H5: a biblioteca os refuta em A6_Finite.lean desde o início e a campanha não os registrava (autópsia do H2, 2026-10-03)
        **{f"f-{h.lower()}-counterexample": (f"CoveringA6.{h}_counterexample", "CoveringLean/A6_Finite.lean", "CoveringLean") for h in ("H1", "H3", "H5")},
        "f-chkn-sound": ("SC.chkN_sound", "CoveringLean/SearchSound.lean", "CoveringLean"),
        "f-cert-of-go": ("CoveringKernel.cert_of_go", "CoveringLean/K3_Bridge.lean", "CoveringLean"),
        "f-syn-cert": ("Syn.syn_cert", "CoveringLean/SynBridge.lean", "CoveringLean"),  # v0.5: a ponte dos certificados por síndromes (alvo padrão)
    }
    for fid, (teo, arq, mod) in medidos.items():
        F.registrar_formal(c, fid, theorem=teo, file=arq, module=mod, raiz_lean=REPO, ator=PROMOTOR, papel="FORMALIZER",
                           rodar_build=lake_ok, lake=None if lake_ok else "/nao/existe/lake")
    # v0.5: os teoremas por síndromes (lib CoveringSyn). Medidos aqui: build do alvo CoveringSyn + `#print axioms` real de cada um.
    for (cel_s, m_s), teo_s in SYN.items():
        F.registrar_formal(c, f"f-syn-{m_s}", theorem=teo_s, file=f"CoveringLean/Syn_K{m_s}.lean", module=f"CoveringLean.Syn_K{m_s}", raiz_lean=REPO,
                           ator=PROMOTOR, papel="FORMALIZER", alvo="CoveringSyn", rodar_build=lake_ok, lake=None if lake_ok else "/nao/existe/lake")
    # tempos/memória medidos à mão por `lake build` (a corrida de `registrar_formal` é incremental: o cache já estava de pé); vêm de _fatos/
    medicoes_lean = {}
    arq_med = raiz_fatos / "medicoes_lean.json"
    if arq_med.is_file():
        medicoes_lean = json.loads(arq_med.read_text(encoding="utf-8"))
        for fid_ in [f["formal_id"] for f in c.listar("formal")]:
            alvo_ = "CoveringSyn" if fid_.startswith("f-syn-") and fid_ != "f-syn-cert" else "padrao"
            if alvo_ in medicoes_lean.get("alvos", {}):
                r_ = c.ler("formal", fid_)
                r_["build_medido_de_zero"] = {"fonte": "campaigns/covering-codes/_fatos/medicoes_lean.json", **medicoes_lean["alvos"][alvo_]}
                c.gravar("formal", fid_, r_, ator=PROMOTOR, papel="FORMALIZER", acao="formal.build_measurement")
    pesados = {
        "f-k2-6-1-eq12": ("SC.K_2_6_1_eq12", "CoveringLean/SearchK6ge12.lean", "CoveringLean.SearchK6ge12",
                          sorted(str(p.relative_to(REPO)) for p in (REPO / "CoveringLean").glob("G610_*.lean"))),
        **{fid_heavy(tag, m_h): (teo_h, arq_h, "CoveringLean." + Path(arq_h).stem,
                                          sorted(str(p.relative_to(REPO)) for p in (REPO / "CoveringLean").glob(f"K3_{tag}*.lean")) +
                                          [f"CoveringLean/C1_Data_{tag}.lean"])
           for (cel_h, m_h), (teo_h, arq_h, tag) in HEAVY.items()},
    }
    # Medição EXTERNA do CoveringHeavy (VM do autor). Entra em `measured_external`, que as guardas NÃO leem: `axioms`, `clean_build` e `lean_version`
    # seguem como a campanha os mediu (nada). Transcrever "clean_build: true" daqui faria a guarda aceitar um valor que a infraestrutura não mediu.
    ext = {}
    arq_ext = raiz_fatos / "medicao_heavy_vm.json"
    if arq_ext.is_file():
        ext = json.loads(arq_ext.read_text(encoding="utf-8"))
    ext_por_teorema = {t["teorema"]: t for t in ext.get("teoremas", [])}

    def medido_externo(teo):
        t = ext_por_teorema.get(teo)
        if not t:
            return None
        extras = [x for x in ext.get("teoremas", []) if x["teorema"] != teo and x["fonte"] == t["fonte"]]
        return {
            "status": "MEASURED_ON_EXTERNAL_VM", "fonte": "campaigns/covering-codes/_fatos/medicao_heavy_vm.json",
            "axioms": t["axiomas"], "fonte_lean": t["fonte"], "lean_version": ext["lean"], "repo_commit": ext["repo_commit"],
            "build_status": f"OK (relato do autor): lake build CoveringHeavy, {ext['jobs_final']} jobs, {ext['folhas_ok']} folhas ok, {ext['folhas_falhou']} falhas",
            "jobs": ext["jobs_final"], "folhas_ok": ext["folhas_ok"], "folhas_falhou": ext["folhas_falhou"],
            "sorry_no_log": ext["sorry_no_log"], "native_decide_ou_ofReduceBool_no_log": ext["native_decide_ou_ofReduceBool_no_log"],
            "inicio_utc": ext["inicio_utc"], "fim_utc": ext["fim_utc"], "relogio_total": ext["relogio_total"],
            "maquina": "VM GCP e2-highmem-8 (8 vCPU, 62 GB), clone limpo da branch da campanha",
            "log_sha256_prefixo": ext["sha256_prefixo_log_completo"], "log_versionado": False,
            "teoremas_adicionais_do_mesmo_arquivo": [{"teorema": x["teorema"], "axioms": x["axiomas"]} for x in extras],
            "ressalva": "Medição do autor em VM; não refeita em segundo ambiente. O `reproduce` local (4 vCPU/15 GB) não consegue refazer. O log completo (1,5 MB) não está "
                        "no repositório: só o prefixo do sha256 e as linhas `#print axioms`. A guarda de formal (model.validar_registro_formal) só aceita o que a campanha mediu, "
                        "então este registro NÃO sustenta promoção (ver _fatos/PROPOSTA_INFRA_medicao_externa.md).",
        }

    for fid, (teo, arq, mod, fontes) in pesados.items():
        achados = F.escanear_fontes(REPO, [arq, *fontes])
        me = medido_externo(teo)
        gravar("formal", fid, {
            "formal_id": fid, "theorem": teo, "module": mod, "file": arq, "lean_root": ".", "lean_version": None,
            "lean_toolchain": ambiente.get("lean_toolchain") or (REPO / "lean-toolchain").read_text().strip(),
            "mathlib_commit": ambiente.get("mathlib_commit"), "manifest_sha256": sha256_arquivo(REPO / "lake-manifest.json"),
            "axioms": None, "declared_axioms": AXIOMAS_DECLARADOS,
            "axioms_status": (f"MEASURED_ON_EXTERNAL_VM: #print axioms {me['axioms']} reportado pelo autor numa VM (commit {me['repo_commit'][:7]}, log sha256 {me['log_sha256_prefixo']}…); "
                              f"NÃO medido por esta campanha nem refeito em segundo ambiente; a guarda não o aceita (axioms=null)") if me else
                             (f"DECLARED_NOT_REPRODUCED: README.md ('Nenhum sorry, nenhum native_decide, e todo #print axioms mostra no máximo propext, Classical.choice, Quot.sound'); "
                              f"o módulo é do alvo CoveringHeavy, custo {CUSTO_HEAVY}: não compilado nesta campanha"),
            "measured_external": me,
            # a execução também vive em kernel_runs/ (nível EXTERNAL_RUN_REPORTED, calculado pela infraestrutura); este campo só aponta
            "kernel_run": KR_HEAVY if me else None,
            "sorry_free": not any(x["kind"] in F.TIPOS_SORRY for x in achados), "sorry_free_basis": f"varredura estática de {len(fontes) + 1} fontes (não é build)",
            "clean_build": False, "build_status": f"NOT_RUN: lake build CoveringHeavy não executado neste ambiente ({CUSTO_HEAVY})"
            + ("; build completo medido só na VM do autor (ver measured_external)" if me else ""),
            "repo_commit": commit, "source_sha256": sha256_arquivo(REPO / arq), "scan_findings": achados, "measured": None,
            "validation_problems": ["axiomas não medidos por esta campanha (declarados" + ("; medidos só na VM externa" if me else "") + ")", "clean_build não medido por esta campanha"]},
            "FORMALIZER", PROMOTOR)

    # ------------------------------------------------------------------ corridas de verificador
    if corridas:
        gerais = ("verify-c", "verify-py-dilation", "verify-rust", "verify-cleanroom")
        pesados_val = VAL_IDS  # só K_7(9,4): q, n cravados no código
        for cel, m, _ in CODIGOS:
            for vid in gerais + tuple(v_ for v_ in pesados_val if aplica(v_, cel)):
                V.rodar(c, vid, wid(cel, m), ator=PROMOTOR, papel="INDEPENDENT_VERIFIER", timeout_s=900)
        for vid in gerais:
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

    # H1, H3, H5: as outras três hipóteses que A6_Finite.lean refuta (autópsia do H2, 2026-10-03). Nasceram fora da campanha: a biblioteca guardava
    # a refutação e o sistema não guardava a hipótese refutada. O enunciado ORIGINAL de cada H não está escrito em nenhum arquivo versionado além do
    # nome e de um comentário de uma linha em A6_Finite.lean; o `statement` abaixo é a leitura do comentário, e o que o Lean refuta LITERALMENTE é o
    # `lean_statement` (copiado do .lean por regex, não digitado). A guarda REFUTED não exige witness porque o claim nunca passou de CONJECTURE.
    lean_a6 = (REPO / "CoveringLean/A6_Finite.lean").read_text()
    HIPOTESES = {
        "H1": ("h1-alpha-nonincreasing",
               "H1: α(q,n,R) = K_q(n,R)·V/q^n é não crescente em n, com q e R fixos (hipótese do autor; texto original não localizado, enunciado lido do comentário "
               "de A6_Finite.lean:95 'H1 says α is nonincreasing in n').",
               {"problem": "H1 de A6_Finite", "domain": "q, R fixos, n variável (contraexemplo em q=2, R=1, n=3→4)", "assumptions": []},
               "α(2,3,1) = 2·4/8 = 1 mas α(2,4,1) = 4·5/16 = 5/4 > 1: α cresce de n=3 para n=4 (K_2(3,1)=2, V=4; K_2(4,1)=4, V=5)."),
        "H3": ("h3-alpha-le-2",
               "H3: α(q,n,R) = K_q(n,R)·V/q^n ≤ 2 para todo (q,n,R) (hipótese do autor; texto original não localizado, o '2' e a desigualdade são lidos do "
               "cabeçalho de A6_Finite.lean:102 'α = 19/9 > 2').",
               {"problem": "H3 de A6_Finite", "domain": "todo (q,n,R) (contraexemplo em q=3, n=3, R=2)", "assumptions": []},
               "α(3,3,2) = 3·19/27 = 19/9 > 2 (K_3(3,2)=3, V=19, q^n=27)."),
        "H5": ("h5-ceil-bound-needs-perfect",
               "H5: se V ∤ q^n então K_q(n,R) > ⌈q^n/V⌉, isto é, a cota de esfera com teto só é atingida por códigos perfeitos (hipótese INFERIDA do enunciado "
               "que o Lean refuta e de A2_Sphere `no_perfect`; texto original não localizado).",
               {"problem": "H5 de A6_Finite", "domain": "todo (q,n,R) com V ∤ q^n (contraexemplo em q=2, n=2, R=1)", "assumptions": []},
               "K_2(2,1) = 2 = ⌈4/3⌉ com V = 3 ∤ 4: o teto é atingido sem código perfeito."),
    }
    for h, (cid_h, enun_h, scope_h, desc_h) in HIPOTESES.items():
        m_lean = re.search(rf"theorem {h}_counterexample :.*?:=", lean_a6, re.S)
        assert m_lean, f"não achei o enunciado de {h}_counterexample em A6_Finite.lean"
        lean_stmt = " ".join(m_lean.group(0).split())
        fid_h, cxid_h = f"f-{h.lower()}-counterexample", f"cx-{cid_h}"
        c.gravar("counterexamples", cxid_h, {
            "counterexample_id": cxid_h, "claim_id": cid_h, "kind": "instance",
            "description": f"{desc_h} (CoveringA6.{h}_counterexample, medido no kernel; todo o resto vem de A6_Finite.lean, sem busca).",
            "witness_id": None, "data": {"formal": fid_h, "lean_statement": lean_stmt}, "created_by": AUTOR, "created": c.meta()["created"]},
            ator=AUTOR, papel="COUNTEREXAMPLE_HUNTER")
        novo(cid_h, enun_h, scope_h, kind="conjecture")
        K.atualizar(c, cid_h, ator=AUTOR, papel="PROPOSER", statement_provenance="enunciado original não localizado em arquivo versionado; ver descrição",
                    refuting_lean_statement=lean_stmt)
        anexa(cid_h, "formal", fid_h)
        K.mudar_estado(c, cid_h, "CONJECTURE", ator=AUTOR, papel="PROPOSER", motivo="hipótese registrada para ser refutada")
        if not validar_registro_formal(c.ler("formal", fid_h)):  # só refuta se o contraexemplo formal foi MEDIDO
            K.invalidar(c, cid_h, cxid_h, ator=PROMOTOR, papel="COUNTEREXAMPLE_HUNTER", motivo=f"{h}_counterexample medido no kernel")

    # K_7(9,4), K_7(8,3) e as demais células: as pontes do Lean
    novo("cert-of-go-lemma", "CoveringKernel.cert_of_go: a checagem booleana `go` verdadeira sobre uma lista estritamente crescente de M inteiros < q^n dá C com |C|=M e Covers R C.",
         {"problem": "ponte checagem -> Covers (certificados por prefixos, CoveringHeavy)", "domain": "K3_Bridge", "assumptions": []}, kind="lemma", trust_boundary=TB_LEAN)
    cx("cert-of-go-lemma", "lema provado no kernel", "nenhum")
    anexa("cert-of-go-lemma", "formal", "f-cert-of-go")
    promover("cert-of-go-lemma", "PROVED", "FORMALIZER", "registro formal medido válido")
    novo("syn-cert-lemma", "Syn.syn_cert: as checagens booleanas por síndromes (okT, okO, okB) e a lista L (unpack = L, estritamente crescente, < q^n, |L| = M) dão "
         "∃ C : Finset (Fin n → ZMod q), C.card = M ∧ Covers R C (SynBridge.lean).",
         {"problem": "ponte certificado por síndromes -> Covers (CoveringSyn)", "domain": "SynBridge", "assumptions": ["NeZero q"]}, kind="lemma", trust_boundary=TB_LEAN)
    cx("syn-cert-lemma", "lema provado no kernel", "nenhum")
    anexa("syn-cert-lemma", "formal", "f-syn-cert")
    promover("syn-cert-lemma", "PROVED", "FORMALIZER", "registro formal medido válido")

    for cel, m, no_readme in CODIGOS:
        q, n, r = CELULAS[cel]
        cid = f"{cel}-ub-{m}"
        e_syn, e_heavy = (cel, m) in SYN, (cel, m) in HEAVY
        deps = (["syn-cert-lemma"] if e_syn else []) + (["cert-of-go-lemma"] if e_heavy else [])
        nota = "" if no_readme else " NÃO consta no README/paper: está em data/codes e docs/code-format.md; novidade não conferida na literatura."
        tb_lean = []
        if e_syn:
            tb_lean += tb((f"{SYN[(cel, m)]} (lib CoveringSyn): axiomas MEDIDOS nesta campanha (f-syn-{m})", "que existe C com |C| = M e Covers R C, no kernel do Lean"),
                          (f"CoveringLean/SynData_K{m}.lean == witness (medido: exp-lean-syn-data-equals-witness-{m})", "elo entre o teorema e o arquivo"))
        if e_heavy:
            tb_lean += tb((f"Lean kernel ({HEAVY[(cel, m)][0]}), medido só na VM do autor (MEASURED_ON_EXTERNAL_VM), não reproduzido aqui ({CUSTO_HEAVY})", "mesmo código, certificado por prefixos"))
        novo(cid, f"Existe código C em (Z_{q})^{n} com |C| = {m} que cobre com raio {r} (data/codes/{nome_codigo(cel, m)}.txt).{nota}",
             {"problem": f"K_{q}({n},{r}) <= {m}", "domain": f"q={q}, n={n}, R={r}", "assumptions": [], "parameters": {"q": q, "n": n, "R": r, "M": m}},
             kind="theorem", depends_on=deps, bound=bound_(cel, m, "upper"),
             trust_boundary=TB_C + tb_lean + tb(("literatura registrada (Kéri/Marosi), declarada", "só para a afirmação de que o valor é menor que o anterior, que o Lean não checa")))
        cx(cid, "claim de existência: o witness é o certificado; verificadores independentes procuram ponto descoberto (uncovered=0)", "uncovered=0 nos verificadores")
        anexa(cid, "witnesses", wid(cel, m))
        anexa(cid, "experiments", PRODUZIDO_POR.get((cel, m), "exp-prior-search-unrecorded"))
        anexa(cid, "literature", f"lit-keri-{cel}-ub")
        if cel == "k7-9-4":
            for v_ in ("v1", "v2", "v3"):
                anexa(cid, "literature", f"lit-marosi-2608-19872-{v_}")
            anexa(cid, "experiments", "exp-state-of-art-crosscheck")
        if e_syn:
            anexa(cid, "experiments", f"exp-lean-syn-data-equals-witness-{m}")
            anexa(cid, "formal", f"f-syn-{m}")
        if e_heavy:
            if e_syn:  # o Lean MEDIDO sustenta o claim; o pesado fica ao lado, declarado (o registro inválido dele travaria PROVED se estivesse em evidence.formal)
                K.atualizar(c, cid, ator=AUTOR, papel="PROPOSER", complementary_formal=[fid_heavy(HEAVY[(cel, m)][2], m)],
                            complementary_formal_note="teorema por prefixos (CoveringHeavy) medido só na VM do autor (measured_external), não reproduzido aqui; fica fora de evidence.formal de propósito")
            else:
                anexa(cid, "formal", fid_heavy(HEAVY[(cel, m)][2], m))
        if (cel, m) == ("k7-9-4", 1351):
            anexa(cid, "experiments", "exp-lean-data-equals-witness-1351")
        anexa(cid, "experiments", "exp-structure-regeneration")
        if corridas:
            negado = promover(cid, "INDEPENDENTLY_REPRODUCED", "INDEPENDENT_VERIFIER", "verificadores de autores/grupos distintos, PASS válido e sem desacordo, neste run")
            if negado:  # a evidência não sustenta IR: o estado honesto é o de baixo (EMPIRICAL: witness + busca de contraexemplo), nunca forçado
                promover(cid, "EMPIRICAL", "PROPOSER", "witness conferido pelo verificador oficial; independência negada pela guarda (ver blocked_independently_reproduced)")
            elif e_syn:
                promover(cid, "PROVED", "FORMALIZER", f"{SYN[(cel, m)]} medido no kernel (axiomas só os esperados) + verificadores independentes (a guarda de PROVED exige os dois)")
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

    # ------------------------------------------------------------------ execução externa do kernel (eixo kernel_runs/, não é estado de claim)
    # A execução histórica do CoveringHeavy na VM. Registrada SÓ com o que a evidência já registrada diz (medicao_heavy_vm.json) mais o que o
    # git do commit verificado responde (toolchain, manifesto, hash de cada fonte NAQUELE commit). Nada é inventado: o log bruto (~/heavy.log) não
    # foi persistido e só existe o prefixo do sha256, então `raw_log.persisted=false` e a infraestrutura calcula EXTERNAL_RUN_REPORTED, nunca
    # KERNEL_VERIFIED. Nenhum claim muda de estado por causa disto (as guardas não leem kernel_runs/).
    heavy_claims = sorted({"k2-6-1-lb-12", "k2-6-1-eq-12"} | {cl["claim_id"] for cl in c.listar("claims")
                          if any(f_.startswith("f-heavy-") for f_ in cl["evidence"]["formal"] + cl.get("complementary_formal", []))})
    if ext:
        def no_commit(rel):
            r_ = subprocess.run(["git", "show", f"{ext['repo_commit']}:{rel}"], cwd=REPO, capture_output=True)
            if r_.returncode != 0:
                raise SystemExit(f"erro: {rel} não existe no commit {ext['repo_commit'][:7]} da medição externa (o commit verificado tem de estar no histórico)")
            return r_.stdout
        manifesto = json.loads(no_commit("lake-manifest.json"))
        mathlib_rev = next(p_["rev"] for p_ in manifesto["packages"] if str(p_.get("name", "")).lower() == "mathlib")
        no_commit("tools/heavy_build_limitado.sh")  # o comando registrado existe nesse commit
        t_ini, t_fim = (__import__("datetime").datetime.strptime(ext[k], "%Y-%m-%dT%H:%M:%SZ") for k in ("inicio_utc", "fim_utc"))
        teoremas_kr = [{"theorem": t_["teorema"], "axioms": t_["axiomas"], "source_file": t_["fonte"].split(":")[0],
                        "source_sha256": hashlib.sha256(no_commit(t_["fonte"].split(":")[0])).hexdigest(),
                        "source_sha256_basis": f"git show {ext['repo_commit'][:7]}:{t_['fonte'].split(':')[0]}",
                        "print_axioms_output": None, "print_axioms_output_note": "a saída literal não foi guardada; só a lista de axiomas do relato"}
                       for t_ in ext["teoremas"]]
        KR.gravar_corrida(c, {
            "schema": KR.SCHEMA, "run_id": KR_HEAVY, "claim_ids": heavy_claims, "commit_sha": ext["repo_commit"], "lean_version": ext["lean"],
            "lean_version_basis": "lean-toolchain do commit (o `lean --version` literal da VM não foi guardado)",
            "lean_toolchain": no_commit("lean-toolchain").decode().strip(), "mathlib_commit": mathlib_rev,
            "command": ["sh", "tools/heavy_build_limitado.sh", "4"], "target": "CoveringHeavy",
            # PROVENIÊNCIA DO HOST: NÃO capturada. Em 2026-10-04 a execução foi feita sem o coletor (que ainda não existia) e o `numeric_instance_id`
            # real da lean-build2 nunca foi lido do servidor de metadados. IP, tipo de máquina ou nome vistos num inventário do GCP NÃO são o id da
            # instância e não entram aqui: nada se fabrica. Por isso a execução continua EXTERNAL_RUN_REPORTED mesmo que o log fosse persistido.
            "host": {"class": "gcp-e2-highmem-8", "id": "lean-build2", "provider": "GCP", "vcpu": 8, "ram_gb": 62, "note": "VM sob demanda, ligada só para este build",
                     "provenance": {"schema": KR.SCHEMA_HOST_PROV, "captured_by_tool": False, "captured_at": None, "source": "none (execução histórica anterior ao coletor)",
                                    "provider": None, "project_id": None, "numeric_instance_id": None, "instance_name": None, "zone": None, "machine_type": None,
                                    "cpu_platform": None, "boot_image": {"source_image": None, "digest": None},
                                    "campos_ausentes": ["numeric_instance_id", "project_id", "instance_name", "zone", "machine_type", "cpu_platform", "boot_image"],
                                    "registrado_de_outro_host": True,
                                    "nota": "O id numérico da instância lean-build2 NÃO foi capturado; host.id acima é só texto declarado pelo autor."}},
            "toolchain_provenance": {"schema": KR.SCHEMA_TOOLCHAIN_PROV, "captured_by_tool": False, "captured_at": None, "lean_version_literal": None,
                                     "lake_version_literal": None, "lean_toolchain_sha256": None, "lake_manifest_sha256": None, "commit_sha": None, "tree_sha": None,
                                     "tree_clean": None, "campos_ausentes": ["lean_version_literal", "lake_version_literal", "lean_toolchain_sha256", "lake_manifest_sha256",
                                                                            "commit_sha", "tree_sha", "tree_clean"],
                                     "nota": "O `lean --version` literal da VM e a limpeza da árvore não foram guardados; o commit e o lean-toolchain vêm do relato "
                                             "(lean_version_basis) e do git do commit verificado, não de medição na VM."},
            "started_at": ext["inicio_utc"], "finished_at": ext["fim_utc"], "duration_s": (t_fim - t_ini).total_seconds(),
            "build": {"status": "OK", "jobs": ext["jobs_final"], "leaves": ext["folhas_ok"], "failures": ext["folhas_falhou"]},
            "sorry_count": ext["sorry_no_log"], "native_decide_policy": "forbidden", "native_decide_count": ext["native_decide_ou_ofReduceBool_no_log"],
            "axioms_allowlist": AXIOMAS_DECLARADOS, "theorems": teoremas_kr,
            "measured_by": {"author": "autor da sessão de 2026-10-04 (o mesmo autor dos claims; sem identidade registrada além do commit)",
                            "origin": "relato do autor da execução na VM, transcrito em _fatos/medicao_heavy_vm.json"},
            "independent_reproduction": False,
            "raw_log": {"sha256": None, "sha256_prefix": ext["sha256_prefixo_log_completo"], "size_bytes": None, "persisted": False, "uri": None,
                        "storage": "nenhum: ~/heavy.log na VM lean-build2 (18 619 linhas, ~1,5 MB) nunca foi copiado para fora da VM; não há hash de 64 hex",
                        "local_sha256_calculado": None},
            "fonte": "campaigns/covering-codes/_fatos/medicao_heavy_vm.json",
            "migracao": "conservadora: EXTERNAL_RUN_REPORTED por falta de log bruto persistido, de saída literal de #print axioms e de proveniência capturada (host e toolchain); não há segunda execução",
        }, ator=PROMOTOR, papel="FORMALIZER")

    # ------------------------------------------------------------------ o traçador: DUAS execuções reais, em VMs distintas (teste ponta a ponta de 2026-10-04)
    # Alvo CoveringLean.Syn_K1887 (claim k7-8-3-ub-1887). Tudo vem dos arquivos de _fatos/kernel_runs_tracer/{a,b} (log bruto, prov.json gerado NA VM pela
    # ferramenta, spec.json); o nível (KERNEL_VERIFIED / KERNEL_INDEPENDENTLY_REPRODUCED) é CALCULADO pela infraestrutura, nunca escrito aqui. Nenhum claim muda de
    # estado (as guardas não leem kernel_runs/). `a/spec_tentativa_copia_da_mesma_execucao.json` NÃO é registrado: é só a tentativa de quebrar do teste.
    # LIMITE: "capturada" (pela ferramenta) não é "atestada"; o log foi enviado ao GCS por outro processo e só o `conferido_por` abaixo diz quem viu o objeto.
    for lado in ("a", "b"):
        pasta_tr = raiz_fatos / "kernel_runs_tracer" / lado
        spec_tr = json.loads((pasta_tr / "spec.json").read_text(encoding="utf-8"))
        log_tr = pasta_tr / "build.log"
        sha_tr = sha256_arquivo(log_tr)
        KR.registrar_execucao(
            c, spec_tr["run_id"], log=log_tr, claim_ids=spec_tr["claim_ids"], teoremas=spec_tr["teoremas"], commit_sha=spec_tr["commit_sha"],
            lean_version=spec_tr["lean_version"], lean_toolchain=spec_tr["lean_toolchain"], mathlib_commit=spec_tr["mathlib_commit"],
            command=spec_tr["command"], target=spec_tr["target"], host=spec_tr["host"], started_at=spec_tr["started_at"], finished_at=spec_tr["finished_at"],
            leaves=spec_tr["leaves"], measured_by=spec_tr["measured_by"],
            armazenador=KR.ArmazenadorPreEnviado(
                f"{TRACER_BUCKET}/{sha_tr}.log", log_tr.stat().st_size,
                "sessão Claude 2026-10-04 via factory-01: upload com token de service account em memória; GET de metadados do objeto confirmou o tamanho 12622",
                "2026-10-04 (hora do GET não registrada)"),
            ator="agente-kr", papel="FORMALIZER", raiz_fontes=REPO, proveniencia_json=pasta_tr / "prov.json")

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

    residuo("res-a6d-searchheavy", kind="fora_da_biblioteca", file="CoveringLean/A6d_SearchHeavy.lean", instances=["k2-6-1"],
            reason="DECLARADO: não compila (README:71, obsoleto com A6e e SearchK6ge12). Não executado aqui (risco de OOM). Célula: K_2(6,1) >= 11 (cabeçalho do arquivo).",
            next_step="apagar (pelo templo: com volta) ou arquivar")
    residuo("res-a5b-stress", kind="fora_da_biblioteca", file="CoveringLean/A5b_Stress.lean", instances=[],
            instances_note="o arquivo trata q=2, n=3, R=1, que não é célula do universo desta campanha",
            reason="DECLARADO: não compila (README:71). MEDIDO: `lake env lean` terminou com rc 137 (SIGKILL) em <=110 s; causa (OOM?) não investigada.",
            next_step="investigar e consertar, ou arquivar")
    # claims cujo teorema Lean só existe como DECLARADO (CoveringHeavy) ou tem uma segunda prova pesada declarada ao lado da medida
    sem_medido = sorted(x for x in heavy_claims if c.ler("claims", x)["status"] not in ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED"))
    residuo("res-heavy-build-not-reproduced", kind="nao_reproduzido", claim_ids=heavy_claims, instances=celulas_de(heavy_claims),
            reason=f"lake build CoveringHeavy ({CUSTO_HEAVY}) não é executável neste container (4 vCPU/15 GB). Os {len(HEAVY) + 1} teoremas têm UMA medição externa do autor numa VM "
                   f"(_fatos/medicao_heavy_vm.json: {ext.get('jobs_final')} jobs, {ext.get('folhas_ok')} folhas ok, {ext.get('folhas_falhou')} falhas, axiomas só propext/Classical.choice/Quot.sound, "
                   f"commit {str(ext.get('repo_commit'))[:7]}, log sha256 {ext.get('sha256_prefixo_log_completo')}…, log não versionado), não refeita em segundo ambiente e não medida por esta campanha: "
                   f"as guardas de formal não a aceitam como registro Lean medido; ela está registrada em kernel_runs/{KR_HEAVY} no nível EXTERNAL_RUN_REPORTED (só o autor atesta: log bruto NÃO persistido, "
                   f"sem hash de 64 hex, sem saída literal de #print axioms; abaixo de KERNEL_VERIFIED) e NÃO é reprodução independente. Sem teorema Lean MEDIDO pela campanha "
                   f"(ficam abaixo de PROVED por isso): {sem_medido}. O 1351 de K_7(9,4) tem também o teorema por síndromes medido (Syn.K7_9_4_le_1351_syn).",
            next_step="(a) KERNEL_VERIFIED: refazer o build numa VM gerando o log, guardá-lo fora do Git e registrar com kernel.registrar_execucao (CLI: `kernel-run register`; hash de 64 hex, uri, saída real de #print axioms); "
                      "(b) KERNEL_INDEPENDENTLY_REPRODUCED: uma SEGUNDA execução completa noutra VM (host.id, run_id e log distintos, mesmo commit); (c) ou refazer pela própria campanha com formal.registrar_formal numa máquina com RAM >= 9 GB (ou provar por síndromes: scripts/syndrome/gen_syn.py, minutos). Ver docs/matematica/ESCADA_DE_EVIDENCIA.md da infraestrutura")
    residuo("res-ci-sem-coveringsyn", kind="garantia_continua", claim_ids=sorted(f"{cc}-ub-{mm}" for (cc, mm) in SYN), instances=sorted({cc for (cc, _) in SYN}),
            reason="VALIDATION.md (achado de processo): o CI do repositório só roda `lake build` do alvo padrão. MEDIDO em .github/workflows/verify-codes.yml: nenhum job constrói CoveringSyn, "
                   "então os cinco teoremas Syn_K* são medidos aqui (esta campanha) mas não recompilados a cada commit.",
            next_step="um job com `lake build CoveringSyn` (alto risco pela classe do AGENTS.md: .github/workflows é do Thiago)")
    residuo("res-search-kit-not-in-repo", kind="geracao_nao_reproduzivel", claim_ids=["k7-9-4-ub-1141", "k7-9-4-ub-1137"], instances=["k7-9-4"],
            reason="a busca dos remendos de 1141 e 1137 (kit de busca, branch feat/kit-de-busca, commit be52cc2) não está neste repositório e nenhum comando/seed foi registrado; "
                   "p1137.json regenera o MESMO conjunto de 1137 palavras (exp-k7-9-4-1137-regen), 1141 não tem p1141.json. A varredura de bases está em audit/k794-base-sweep.",
            next_step="versionar o kit de busca (ou o comando e a semente) ou registrar p1141.json")
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
        "k7-9-4": ("1137, 1141, 1285 e 1351 estão abaixo do 1475 do Marosi (v2/v3), mas: (1) Cohen-Honkala-Litsyn-Lobstein 1997 e Östergård 1999 não foram lidos; (2) trabalho de "
                   "Östergård/Rivas Soriano posterior a 2011 e não indexado no arXiv; (3) os quatro códigos só foram verificados por programas deste repositório (verify.c, dilatação, "
                   "verify-rust, clean-room e, no main v0.5, A/B/C de verification/, do mesmo autor de verify.c); rodar o verify_cov.py do Marosi daria independência real, mas é CÓDIGO "
                   "DE TERCEIROS e NÃO foi executado (precisa de autorização); (4) a busca que produziu p1285.json/p1137.json/o 1141 não é reprodutível (sem comando/seed/log: res-search-kit-not-in-repo); "
                   "(5) STATE_OF_ART.md (revisão de 2026-10-02) não achou nada <= 1137, mas ele mesmo lista o que não checou (Google Scholar, bases pagas, teses, periódico); ver exp-state-of-art-crosscheck; (6) RISCO: pela ADS (Lobstein-van Wee) K_7(9,4) <= 931 (=19*343/7) e <= 1225, <= 1344, mas SÓ SE existirem códigos normais "
                   "para as cotas tabeladas; a busca por componentes normais falhou (LITERATURA_PROFUNDA.md §1.3) e nada disso é predecessor registrado. 931 < 1137: se fosse realizável, "
                   "tiraria até o 1137",
                   "autorizar e rodar verify_cov.py sobre data/codes/q7_n9_R4_M1137.txt; ler Cohen et al. 1997 e Östergård 1999; registrar o comando da busca dos remendos"),
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
    bloqueados = [x for x in ub_claims if c.ler("claims", x)["status"] not in ("INDEPENDENTLY_REPRODUCED", "PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED")]
    if bloqueados:
        residuo("res-reverify-independent-author", kind="independencia", claim_ids=bloqueados, instances=celulas_de(bloqueados),
                reason="MEDIDO pela guarda de INDEPENDENTLY_REPRODUCED neste run: " + " | ".join(c.ler("claims", bloqueados[0]).get("blocked_independently_reproduced", ["(sem motivo gravado)"])),
                next_step="outro agente/humano (diferente do autor dos claims e do autor de cada verificador já contado) escreve ou reimplementa um verificador, registra com implemented_by verdadeiro")
    residuo("res-validation-independence-wording", kind="independencia", claim_ids=[x for x in ub_claims if x.startswith("k7-9-4-ub-")], instances=["k7-9-4"],
            reason=f"VALIDATION.md e o paper dizem 'três verificadores independentes' (A, B, C de verification/). MEDIDO no git log: os três vieram de UM commit e do MESMO autor ({autor_val}) de "
                   "tools/verify/verify.c, então a guarda de independência os conta num componente só com verify-c. A independência de AUTORIA que a campanha mede vem de verify-rust e "
                   "verify-cleanroom (autoria distinta declarada nos READMEs; o git log assina 'Claude' nos dois). Os A, B, C são independentes de MÉTODO (força bruta, união de bolas, BFS) e de "
                   "código, não de autoria. A frase só vale nesse sentido.",
            next_step="o dono decide se a frase do paper/VALIDATION.md passa a dizer 'independentes de método'; ou outro autor reescreve um dos três")
    ler_ = lambda rel: (REPO / rel).read_text(encoding="utf-8")  # noqa: E731
    if re.search(r"ainda não são teoremas Lean", ler_("README.md")):
        residuo("res-readme-stale-lean", kind="inconsistencia", instances=sorted({cc for (cc, mm) in HEAVY if (cc, mm) not in SYN}),
                reason="README.md (seção 'Resultados da v0.3') ainda diz dos outros 7 códigos de data/codes que 'ainda não são teoremas Lean', mas a tabela da v0.5 do MESMO arquivo lista "
                       "`CoveringKernel.K*_kernel` para cada um deles (e `Syn.K7_8_3_le_1887_syn`). O texto está obsoleto; a campanha segue os arquivos .lean, não o texto.",
                next_step="o dono corrige o parágrafo da v0.3 do README")

    # ------------------------------------------------------------------ universo (finito) e cobertura
    # Os números do universo são DERIVADOS do estado dos claims (nada digitado): ub_formal_lean = menor M de claim de cota superior que chegou a PROVED+ (teorema Lean
    # MEDIDO); lb_formal_melhor = maior cota inferior de claim PROVED+. O lb 12 de K_2(6,1) é declarado/exaustivo (Lean pesado não reproduzido), por isso NÃO entra em lb_formal_melhor.
    FORTES = ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED")
    FRACOS_OK = FORTES + ("INDEPENDENTLY_REPRODUCED",)
    todos_claims = c.listar("claims")

    def melhor(cel_, direcao, estados, fn):
        vs = [cl["bound"]["value"] for cl in todos_claims if cl.get("bound") and cl["status"] in estados and cl["bound"]["direction"] == direcao
              and cel_de(cl["bound"]["parameters"]["q"], cl["bound"]["parameters"]["n"], cl["bound"]["parameters"]["R"]) == cel_]
        return fn(vs) if vs else None
    inst = []
    for cel, (q, n, r) in CELULAS.items():
        inst.append({"id": cel, "q": q, "n": n, "R": r, "lb_formal_esfera": LB_ESFERA.get(cel), "lb_formal_melhor": melhor(cel, "lower", FORTES, max),
                     "ub_verificado_melhor": melhor(cel, "upper", FRACOS_OK, min), "ub_formal_lean": melhor(cel, "upper", FORTES, min),
                     "size": n})  # o 264 do paper continua fora do universo; a fonte agora é lit-keri-k7-9-4-lb (Kéri, chave m)
    COV.definir_universo(c, {"tipo": "finito", "total": len(inst), "instancias": inst, "estado_minimo_resolvido": "EXHAUSTIVE_BOUNDED",
                             "descricao": "Células (q,n,R) tratadas pela campanha: 8 da cota de esfera (7 com código verificado + K_7(9,4)) e K_2(6,1). "
                                          "'Resolvida' = K_q(n,R) determinado (lb = ub). Só K_2(6,1). As demais têm faixa [lb, ub] aberta."},
                         ator=AUTOR, papel="COORDINATOR")

    # ------------------------------------------------------------------ reproduce.json
    k794_wits = [wid(cel, m) for cel, m, _ in CODIGOS if cel == "k7-9-4"]
    passos = [
        {"id": "ambiente", "type": "ambiente", "requires": ["cc", "python3", "go", "rustc", "cargo", "pytest"], "report_versions": ["cc", "python3", "go", "rustc"]},
        {"id": "hashes-dos-witnesses", "type": "hashes"},
        {"id": "check-all-verify-c", "type": "dados", "command": ["bash", "tools/verify/check_all.sh"], "timeout_s": 600},
        {"id": "estrutura-regenera", "type": "gerador", "command": ["python3", "scripts/codes/build_structured.py", "--check"], "timeout_s": 600},
        {"id": "gerador-1285", "type": "gerador", "command": ["python3", "-m", "unittest", "tests.test_code_format.GeneratorsRegenerateTheCodes", "-v"], "timeout_s": 600},
        {"id": "gerador-1137", "type": "gerador", "command": ["python3", "scripts/search/gen.py", "data/search/p1137.json", "/tmp/covering_p1137_regen.txt"], "timeout_s": 120},
        {"id": "espelho-busca-k2-6-1", "type": "gerador", "command": ["python3", "scripts/k261/sc_ref.py", "6", "10", "2"], "timeout_s": 120},
        # pytest, não unittest: test_ledger/test_publish/test_record_loop importam módulos por tests/conftest.py (medido: `unittest discover` dá 3 erros de import)
        {"id": "testes-pytest", "type": "teste", "command": ["python3", "-m", "pytest", "-q", "tests"], "timeout_s": 1800},
        {"id": "verificadores-gerais-sobre-witnesses", "type": "verificadores", "verifiers": ["verify-c", "verify-py-dilation", "verify-rust", "verify-cleanroom"]},
        *([{"id": "verificadores-k794-sobre-witnesses-k7-9-4", "type": "verificadores", "verifiers": list(VAL_IDS), "subjects": k794_wits}]
          if REGISTRAR_VERIFICATION_DO_MAIN else []),
        {"id": "lake-build-alvo-padrao", "type": "lean_build", "lean_root": ".", "target": None, "opcional": True,
         "nota": "alvo padrão CoveringLean (8944 jobs, com SynCheck/SynBridge)"},
        {"id": "lake-build-coveringsyn", "type": "lean_build", "lean_root": ".", "target": "CoveringSyn", "opcional": True,
         "nota": "os cinco teoremas por síndromes (~10 min de relógio); CoveringHeavy (~9,3 h de CPU) NÃO está aqui"},
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
