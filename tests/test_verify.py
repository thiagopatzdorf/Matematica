"""Verificador oficial tools/verify/verify.c: positivos para todo data/codes, negativos por defeito.

Roda com:  python3 -m unittest discover -s tests -v   (precisa de um compilador C: cc/gcc)
"""
import glob
import hashlib
import itertools
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = sorted(glob.glob(os.path.join(ROOT, "data", "codes", "*.txt")))


def lines_of(path):
    with open(path) as f:
        return f.read().split()


def canon(lines):
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()


def params(path):
    return tuple(int(x) for x in re.findall(r"\d+", os.path.basename(path)))


class VerifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.bin = os.path.join(cls.tmp, "verify")
        cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
        subprocess.run([cc, "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", cls.bin,
                        os.path.join(ROOT, "tools/verify/verify.c")], check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def run_lines(self, path, lines, extra=()):
        q, n, R, _ = params(path)
        r = subprocess.run([self.bin, "-q", str(q), "-n", str(n), "-r", str(R), *extra, "-"],
                           input="\n".join(lines) + "\n", capture_output=True, text=True)
        return r

    @staticmethod
    def field(out, key):
        return re.search(rf"\b{key}=(\S+)", out).group(1)

    # ------------------------------------------------------------------ positivos
    def test_every_code_covers_and_reports_the_python_canonical_sha256(self):
        for path in CODES:
            with self.subTest(code=os.path.basename(path)):
                r = subprocess.run([self.bin, path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(self.field(r.stdout, "uncovered"), "0")
                self.assertEqual(self.field(r.stdout, "sha256"), canon(lines_of(path)))
                self.assertEqual(int(self.field(r.stdout, "M")), params(path)[3])

    def test_uncovered_count_matches_an_independent_python_check(self):
        # verificação por força bruta, escrita sem nada do C: distância de Hamming ponto a ponto
        path = os.path.join(ROOT, "data/codes/q5_n7_R2_M500.txt")
        q, n, R, _ = params(path)
        words = lines_of(path)[1:]  # sem a primeira palavra, para ter pontos descobertos
        C = [tuple(map(int, w)) for w in words]
        unc = sum(1 for x in itertools.product(range(q), repeat=n)
                  if all(sum(a != b for a, b in zip(x, c)) > R for c in C))
        r = self.run_lines(path, words)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(int(self.field(r.stdout, "uncovered")), unc)
        self.assertGreater(unc, 0)

    # ------------------------------------------------------------------ negativos
    def test_removing_one_word_leaves_points_uncovered(self):
        for path in CODES:
            with self.subTest(code=os.path.basename(path)):
                r = self.run_lines(path, lines_of(path)[1:])
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertGreater(int(self.field(r.stdout, "uncovered")), 0)

    def test_duplicate_word_is_an_error(self):
        path = os.path.join(ROOT, "data/codes/q7_n9_R4_M1351.txt")
        L = lines_of(path)
        r = self.run_lines(path, L + [L[5]])
        self.assertEqual(r.returncode, 2)
        self.assertIn("duplicada", r.stderr)

    def test_digit_not_below_q_is_an_error(self):
        path = os.path.join(ROOT, "data/codes/q5_n9_R5_M50.txt")
        L = lines_of(path)
        r = self.run_lines(path, L[:-1] + ["5" + L[-1][1:]])
        self.assertEqual(r.returncode, 2)
        self.assertIn("dígito >= q", r.stderr)

    def test_wrong_length_is_an_error(self):
        path = os.path.join(ROOT, "data/codes/q5_n9_R5_M50.txt")
        L = lines_of(path)
        r = self.run_lines(path, L + [L[0] + "0"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("comprimento", r.stderr)

    def test_word_count_different_from_M_is_an_error(self):
        path = os.path.join(ROOT, "data/codes/q5_n9_R5_M50.txt")
        r = self.run_lines(path, lines_of(path), extra=("-m", "49"))
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
