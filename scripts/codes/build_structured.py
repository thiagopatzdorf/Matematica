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
