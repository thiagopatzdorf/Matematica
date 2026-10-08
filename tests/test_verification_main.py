"""Os verificadores que o main v0.5 trouxe (verification/verify_bfs) concordam com o verificador oficial (tools/verify/verify.c) e recusam o que não é o código.

Só o BFS em Rust roda aqui (8 s por execução); o de força bruta (~3 min) e o de bolas (~50 s) ficam na campanha (campaigns/covering-codes) e em
verification/run_all.sh. Cada teste descreve a falha que impede.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W1137 = os.path.join(ROOT, "data", "codes", "q7_n9_R4_M1137.txt")
RUSTC = shutil.which("rustc") or (os.path.expanduser("~/.cargo/bin/rustc") if os.path.exists(os.path.expanduser("~/.cargo/bin/rustc")) else None)
CC = shutil.which("cc")


def field(out, k):
    return next(t.split("=", 1)[1] for t in out.split() if t.startswith(k + "="))


@unittest.skipUnless(RUSTC and CC, "rustc/cc ausentes")
class VerificationBfsAgreesWithOfficialVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="verif_main_")
        cls.bfs = os.path.join(cls.tmp, "verify_bfs")
        cls.c = os.path.join(cls.tmp, "verify")
        subprocess.run([RUSTC, "-O", "-o", cls.bfs, os.path.join(ROOT, "verification", "verify_bfs", "main.rs")], check=True, capture_output=True)
        subprocess.run([CC, "-O2", "-std=c99", "-o", cls.c, os.path.join(ROOT, "tools", "verify", "verify.c")], check=True, capture_output=True)
        with open(W1137) as fh:
            cls.words = [w.strip() for w in fh if w.strip()]
        cls.minus_one = os.path.join(cls.tmp, "minus_one.txt")  # nome neutro: o verify.c não pode ler a instância do nome
        with open(cls.minus_one, "w") as fh:
            fh.write("\n".join(cls.words[1:]) + "\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_1137_witness_passes_in_the_main_bfs_and_in_the_official_verifier(self):
        a = subprocess.run([self.bfs, W1137, "1137"], capture_output=True, text=True)
        b = subprocess.run([self.c, "--q", "7", "--n", "9", "--R", "4", "--M", "1137", W1137], capture_output=True, text=True)
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stderr + b.stderr)
        self.assertIn("uncovered = 0", a.stdout)

    def test_dropping_one_word_leaves_the_same_uncovered_count_in_the_main_bfs_and_in_the_official_verifier(self):
        a = subprocess.run([self.bfs, self.minus_one, "1136"], capture_output=True, text=True)
        b = subprocess.run([self.c, "--q", "7", "--n", "9", "--R", "4", "--M", "1136", self.minus_one], capture_output=True, text=True)
        self.assertEqual((a.returncode, b.returncode), (1, 1), a.stderr + b.stderr)
        n_bfs = int(re.search(r"^uncovered = (\d+)", a.stdout, re.M).group(1))
        self.assertGreater(n_bfs, 0)
        self.assertEqual(n_bfs, int(field(b.stdout, "uncovered")))

    def test_a_wrong_declared_word_count_fails_even_when_the_code_covers(self):
        # o código de 1137 cobre, mas declarar M=1136 é afirmar outra instância: tem de dar FAIL, nunca PASS
        a = subprocess.run([self.bfs, W1137, "1136"], capture_output=True, text=True)
        self.assertEqual(a.returncode, 1)
        self.assertTrue(a.stdout.strip().endswith("FAIL"))


if __name__ == "__main__":
    unittest.main()
