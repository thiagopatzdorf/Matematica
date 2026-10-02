import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
for sub in ("ledger", "scripts/loop", "scripts/publish"):
    sys.path.insert(0, str(RAIZ / sub))

FONTES = RAIZ / "tests" / "fixtures" / "fontes"


@pytest.fixture
def ledger_recortado(tmp_path):
    """Ledger montado só com as fontes recortadas (sem rede), numa cópia em tmp."""
    import build

    ldir = tmp_path / "ledger"
    ldir.mkdir()
    for nome in ("ours.json", "provenance.json", "sources.json"):
        shutil.copyfile(RAIZ / "ledger" / nome, ldir / nome)
    sources = json.loads((ldir / "sources.json").read_text())
    ours = json.loads((ldir / "ours.json").read_text())
    led = build.construir(build.ler_fontes(FONTES, sources), ours, sources)
    build.escrever(led, ldir / "cells.json")
    return ldir
