"""Os números da tabela "Números conferidos" do README saem do ledger e de data/codes, não de memória.

Regra que isto trava: o README já ficou com 520 exatas e 13 teoremas Lean próprios quando o ledger (gerado, com teste próprio) tinha 523 e 14, porque a v0.9
atualizou o ledger e só parte do README. Cada número é recomputado do `ledger/cells.json` e de `data/codes/`; se divergir, o teste diz qual.
"""
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _celulas():
    d = json.loads((RAIZ / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]
    return d if isinstance(d, list) else list(d.values())


def _readme():
    return (RAIZ / "README.md").read_text(encoding="utf-8")


class ReadmeNumerosTest(unittest.TestCase):
    def test_celulas_exatas_e_abertas_do_readme_batem_com_o_ledger(self):
        cs = _celulas()
        exatas = sum(1 for c in cs if c["certification"].get("exact"))
        m = re.search(r"(\d+), das quais (\d+) com valor exato e (\d+) abertas", _readme())
        self.assertIsNotNone(m, "linha das células exatas/abertas sumiu do README")
        self.assertEqual((int(m.group(1)), int(m.group(2)), int(m.group(3))), (len(cs), exatas, len(cs) - exatas),
                         "README com contagem de células diferente do ledger/cells.json")

    def test_teoremas_lean_proprios_do_readme_batem_com_o_ledger(self):
        cs = _celulas()
        proprias = [c for c in cs if c.get("ours_lean")]
        abaixo = [c for c in proprias if c["best"].get("holder") == "ours_lean" and c["best"].get("beats_published")]
        m = re.search(r"células em que temos teorema Lean próprio \| (\d+) \((\d+) abaixo", _readme())
        self.assertIsNotNone(m, "linha dos teoremas Lean próprios sumiu do README")
        self.assertEqual((int(m.group(1)), int(m.group(2))), (len(proprias), len(abaixo)),
                         "README com contagem de teoremas Lean próprios diferente do ledger/cells.json")

    def test_codigos_em_data_codes_do_readme_batem_com_o_diretorio(self):
        n = len(list((RAIZ / "data" / "codes").glob("*.txt")))
        m = re.search(r"códigos em `data/codes/` \| (\d+),", _readme())
        self.assertIsNotNone(m, "linha dos códigos em data/codes sumiu do README")
        self.assertEqual(int(m.group(1)), n, "README com número de códigos diferente de data/codes/")


if __name__ == "__main__":
    unittest.main()
