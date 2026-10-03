"""Guardas do rascunho v0.6 do paper: a tabela vem dos dados, o texto não alega novidade
e as datas das fontes estão no texto."""
import re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = (ROOT / "paper/main.tex").read_text()


class TestPaperV06(unittest.TestCase):
    def test_tabela_do_paper_diverge_dos_dados(self):
        antes = (ROOT / "paper/evidence_table.tex").read_text()
        subprocess.run([sys.executable, str(ROOT / "tools/campaign/paper_table.py")], check=True, capture_output=True)
        self.assertEqual(antes, (ROOT / "paper/evidence_table.tex").read_text(),
                         "paper/evidence_table.tex não corresponde ao snapshot; rode tools/campaign/snapshot_covering.py e paper_table.py")

    def test_texto_alega_novidade_proibida(self):
        for pat in (r"new record", r"new best known", r"state of the art", r"state-of-the-art", r"\bthe first to\b", r"\bfirst[- ]ever\b",
                    r"where the codes are new", r"builds in seconds"):
            self.assertIsNone(re.search(pat, TEX, re.I), pat)

    def test_datas_das_versoes_do_marosi_e_do_keri(self):
        for t in ("1743", "1475", "20 August 2026", "23 August 2026", "2 September 2026", "15 October 2009", "25 November 2011"):
            self.assertIn(t, TEX)

    def test_python_nao_conta_e_mesmo_modelo_nao_e_independencia_total(self):
        tab = (ROOT / "paper/evidence_table.tex").read_text()
        self.assertIn("not counted for independence", tab)
        self.assertIn("full cognitive independence", TEX)

    def test_fontes_nao_lidas_declaradas(self):
        self.assertIn("did not read in the original", TEX)


if __name__ == "__main__":
    unittest.main()
