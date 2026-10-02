"""tools/campaign/verify_cover_dilation.py concorda com o verify.c (oficial) em positivos e em negativos, e rejeita entrada inválida."""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, "tools", "campaign", "verify_cover_dilation.py")
C_SRC = os.path.join(ROOT, "tools", "verify", "verify.c")
SMALL = os.path.join(ROOT, "data", "codes", "q5_n9_R5_M50.txt")


def field(out, k):
    return next(t.split("=", 1)[1] for t in out.split() if t.startswith(k + "="))


class DilationVerifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cbin = os.path.join(cls.tmp.name, "verify")
        subprocess.run(["cc", "-O2", "-std=c99", "-o", cls.cbin, C_SRC], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def words_minus_first(self):
        with open(SMALL) as fh:
            return [w.strip() for w in fh if w.strip()][1:]

    def test_every_small_code_covers_and_prints_the_same_canonical_sha256_as_the_c_verifier(self):
        for name in ("q5_n9_R5_M50", "q5_n7_R2_M500", "q4_n10_R4_M192"):
            path = os.path.join(ROOT, "data", "codes", name + ".txt")
            a = subprocess.run([sys.executable, PY, path], capture_output=True, text=True)
            b = subprocess.run([self.cbin, path], capture_output=True, text=True)
            self.assertEqual((a.returncode, b.returncode), (0, 0), name + a.stderr + b.stderr)
            self.assertEqual(field(a.stdout, "sha256"), field(b.stdout, "sha256"))

    def test_removing_one_word_gives_the_same_uncovered_count_as_the_c_verifier(self):
        words = self.words_minus_first()
        data = "\n".join(words) + "\n"
        a = subprocess.run([sys.executable, PY, "-q", "5", "-n", "9", "-r", "5", "-"], input=data, capture_output=True, text=True)
        b = subprocess.run([self.cbin, "-q", "5", "-n", "9", "-r", "5", "-"], input=data, capture_output=True, text=True)
        self.assertEqual((a.returncode, b.returncode), (1, 1))
        self.assertEqual(field(a.stdout, "uncovered"), field(b.stdout, "uncovered"))
        self.assertGreater(int(field(a.stdout, "uncovered")), 0)

    def test_duplicate_word_and_wrong_m_are_input_errors_not_a_cover_failure(self):
        words = self.words_minus_first()
        r = subprocess.run([sys.executable, PY, "-q", "5", "-n", "9", "-r", "5", "-"], input="\n".join(words + words[:1]),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        r = subprocess.run([sys.executable, PY, "-q", "5", "-n", "9", "-r", "5", "-m", "50", "-"], input="\n".join(words),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
