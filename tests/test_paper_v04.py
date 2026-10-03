"""Guardas do paper v0.4: a tabela vem dos dados, o texto não alega novidade,
e 1285/1887 não são apresentados como teorema Lean enquanto não houver teorema."""
import json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = (ROOT / "paper/main.tex").read_text()


class TestPaperV04(unittest.TestCase):
    def test_tabela_do_paper_diverge_dos_dados(self):
        antes = (ROOT / "paper/evidence_table.tex").read_text()
        subprocess.run([sys.executable, str(ROOT / "tools/campaign/paper_table.py")], check=True, capture_output=True)
        depois = (ROOT / "paper/evidence_table.tex").read_text()
        self.assertEqual(antes, depois, "paper/evidence_table.tex não corresponde ao snapshot; rode tools/campaign/paper_table.py")

    def test_texto_alega_novidade_proibida(self):
        for pat in (r"new record", r"new best known", r"state of the art", r"state-of-the-art", r"\bthe first to\b", r"\bfirst[- ]ever\b", r"\bnovel (code|bound|result)"):
            self.assertIsNone(re.search(pat, TEX, re.I), pat)

    def test_contagem_de_codigos_vem_dos_dados(self):
        rows = json.loads((ROOT / "campaigns/covering-codes/snapshot/SNAPSHOT.json").read_text())["rows"]
        nao_formalizados = [r for r in rows if not r["lean"].startswith("EXISTS")]
        self.assertIn(f"{['zero','one','two','three','four','five','six','seven','eight','nine','ten'][len(nao_formalizados)]} more codes", TEX)
        self.assertNotIn("Seven further codes", TEX)

    def test_1285_e_1887_nao_aparecem_como_teorema_lean(self):
        rows = json.loads((ROOT / "campaigns/covering-codes/snapshot/SNAPSHOT.json").read_text())["rows"]
        for r in rows:
            if r["size"] in (1285, 1887):
                self.assertTrue(r["lean"].startswith("no Lean theorem"), r["witness_id"])
        self.assertIn("no Lean theorem currently exists", TEX)

    def test_python_nao_conta_na_tabela(self):
        self.assertIn("not counted for independence", (ROOT / "paper/evidence_table.tex").read_text())

    def test_datas_das_versoes_do_marosi(self):
        for t in ("1743", "1475", "20 August 2026", "23 August 2026", "2 September 2026", "15 October 2009", "25 November 2011"):
            self.assertIn(t, TEX)


if __name__ == "__main__":
    unittest.main()
