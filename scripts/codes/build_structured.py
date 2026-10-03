#!/usr/bin/env python3
"""Regenera data/structured/*.json a partir de data/codes/*.txt (structure.py + proveniência abaixo).

Uso (da raiz do repo):  python3 scripts/codes/build_structured.py [--check]
--check não grava nada: falha se algum JSON versionado diferir do que seria gerado agora.

A proveniência fica aqui, num lugar só, porque ela não está no .txt: o que não foi registrado na
época fica como null e a nota diz isso (não se inventa origem).
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codefmt as cf  # noqa: E402
import structure as st  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_UNKNOWN = {
    "generator": None,
    "commit": None,
    "seed": None,
    "command": None,
    "date": None,
    "agent": None,
    "repo_commit": "562fa42",
    "notes": "busca anterior à v0.3; o gerador não foi registrado. repo_commit é onde o .txt entrou no repo.",
}

PROVENANCE = {
    "q7_n9_R4_M1351": {
        "generator": "lincov (Mapika/coldcase) para os 3 cosets de [9,3]_7; remendo de 322 palavras sem registro",
        "commit": "56a8cce",
        "seed": None,
        "command": None,
        "date": "2026-10-01",
        "agent": "James.V1",
        "repo_commit": "562fa42",
        "notes": "structure.py mostrou que as 322 palavras do remendo são 46 cosets de uma reta (subcódigo [9,1]_7).",
    },
    "q7_n9_R4_M1285": {
        "generator": "scripts/search/gen.py (3 cosets de [9,3]_7 H=[I6|A] + cosets de subcódigo + palavras soltas)",
        "commit": None,
        "seed": None,
        "command": "python3 scripts/search/gen.py data/search/p1285.json data/codes/q7_n9_R4_M1285.txt",
        "date": "2026-10-02",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "regenerado byte a byte (sha256 do arquivo 89cbd6b2...) a partir de p1285.json, copiado da VM "
                 "lean-build2 (~/h/s2/b). Estrutura registrada com --dims 3,1 para bater com o gerador.",
        "dims": [3, 1],
    },
    "q7_n9_R4_M1141": {
        "generator": "kit de busca do agente E (scripts/search na branch feat/kit-de-busca): enumeração exata das "
                     "6362 classes de [9,3]_7 + otimizador de remendo",
        "commit": None,
        "seed": None,
        "command": None,
        "date": "2026-10-02",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "base H=[I6|A], A=666 065 652 643 621 615, síndromes 0, 7708, 4191 (6 órfãs, 2058 pontos) + 112 "
                 "palavras; achado na VM lean-build2 (~/h/s2/e). Provado no Lean por Syn.K7_9_4_le_1141_syn.",
    },
    "q7_n9_R4_M1137": {
        "generator": "kit de busca do agente E (feat/kit-de-busca be52cc2): mesma base de 6 órfãs do 1141 + "
                     "patch_opt (recozimento, partida do zero) e patch_lns (LNS com ILP exato no HiGHS)",
        "commit": "be52cc2",
        "seed": None,
        "command": None,
        "date": "2026-10-02",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "base H=[I6|A], A=666 065 652 643 621 615, síndromes 0, 7708, 4191 + 108 palavras "
                 "(parâmetros em data/search/p1137.json). Ótimo local exato de remove-2/insere-1. "
                 "Verificado por tools/verify/verify.c e pelo verify.py do kit.",
    },
    "q7_n8_R3_M1887": {
        "generator": "maestro (VM lean-build2, ~/h/s2/maestro): mesmos 5 cosets de [8,3]_7 do 1893 + 172 palavras",
        "commit": None,
        "seed": None,
        "command": None,
        "date": "2026-10-02",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "o .txt daqui está na ordem canônica; o arquivo da VM (sha256 557cf336...) tem outra ordem "
                 "e o mesmo sha256 canônico.",
    },
    "q7_n10_R4_M5667": {
        "generator": "scripts/attack (feat/ataque-celulas-2011): hsearch -> base_search eval t=2 em [10,4]_7 -> "
                     "lift para [10,3]_7 -> coset_sa t=16 -> patch_opt",
        "commit": None,
        "seed": None,
        "command": None,
        "date": "2026-10-03",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "16 classes laterais de um [10,3]_7 (3 síndromes órfãs, 1029 pontos) + 179 palavras. Detalhes e "
                 "síndromes em data/attack/q7_n10_R4_M5667.json. Verificado por scripts/attack/verify_bfs e "
                 "tools/verify/verify.c. Não conferido no Lean.",
        "dims": [3],
    },
    "q5_n11_R4_M2875": {
        "generator": "scripts/attack (feat/ataque-celulas-2011): hsearch -> coset_sa t=4 em [11,4]_5 -> lift para "
                     "[11,3]_5 -> coset_sa t=22 -> coset_wsa (w=21)",
        "commit": None,
        "seed": None,
        "command": None,
        "date": "2026-10-03",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "23 classes laterais de um [11,3]_5, sem remendo. Detalhes em data/attack/q5_n11_R4_M2875.json. "
                 "Verificado por scripts/attack/verify_bfs e tools/verify/verify.c.",
        "dims": [3],
    },
    "q5_n10_R5_M163": {
        "generator": "scripts/attack (feat/ataque-celulas-2011): hsearch t=1 em [10,3]_5 (8 síndromes órfãs) -> "
                     "patch_opt",
        "commit": None,
        "seed": 7,
        "command": "patch_opt base.json --L 0 --W 40 --secs 1500 --seed 7 --T0 1.5 --T1 0.3",
        "date": "2026-10-03",
        "agent": "James.V1",
        "repo_commit": None,
        "notes": "o próprio [10,3]_5 + 38 palavras (cota do LP para o remendo nesta base: 22). Detalhes em "
                 "data/attack/q5_n10_R5_M163.json.",
        "dims": [3],
    },
}


def build(txt: str) -> tuple[str, str]:
    q, n, R, M = cf.parse_cell_name(txt)
    name = os.path.basename(txt)[:-4]
    prov = dict(PROVENANCE.get(name, _UNKNOWN))
    dims = prov.pop("dims", None)
    doc = st.structure(cf.read_txt(txt, q, n), q, n, R, M, prov, dims)
    out = os.path.join(ROOT, "data", "structured", name + ".json")
    return out, cf.dump(doc)


def main(argv=None) -> int:
    check = "--check" in (argv if argv is not None else sys.argv[1:])
    bad = 0
    for txt in sorted(glob.glob(os.path.join(ROOT, "data", "codes", "*.txt"))):
        out, text = build(txt)
        if check:
            cur = None
            if os.path.exists(out):
                with open(out) as f:
                    cur = f.read()
            if cur != text:
                print(f"DIFERE: {out}", file=sys.stderr)
                bad += 1
        else:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as f:
                f.write(text)
        print(f"{os.path.basename(out)}: {st.summary(json.loads(text))}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
