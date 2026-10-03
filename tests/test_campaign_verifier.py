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
        subprocess.run(["cc", "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", cls.cbin, C_SRC], check=True)

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

    # ------------------------------------------------------------------ parâmetros explícitos (red team D-12): os DOIS verificadores concordam
    def both(self, args, data=None, path=SMALL):
        a = subprocess.run([sys.executable, PY, *args, path if data is None else "-"], input=data, capture_output=True, text=True)
        b = subprocess.run([self.cbin, *args, path if data is None else "-"], input=data, capture_output=True, text=True)
        return a, b

    def test_same_code_with_wrong_explicit_parameters_fails_in_both_verifiers(self):
        with open(SMALL) as fh:
            data = "".join(w.strip() + "\n" for w in fh if w.strip())
        explicit = lambda q, n, R, M: ["--q", str(q), "--n", str(n), "--R", str(R), "--M", str(M)]  # noqa: E731
        casos = {  # nome do caso -> (opções, exit esperado nos dois)
            "certo": (explicit(5, 9, 5, 50), 0),
            "R menor (descoberto)": (explicit(5, 9, 2, 50), 1),
            "M-1": (explicit(5, 9, 5, 49), 2),
            "M+1": (explicit(5, 9, 5, 51), 2),
            "n errado (comprimento)": (explicit(5, 8, 5, 50), 2),
            "q errado (dígito >= q)": (explicit(4, 9, 5, 50), 2),
        }
        for nome, (opts, esperado) in casos.items():
            with self.subTest(caso=nome):
                a, b = self.both(opts, data)
                self.assertEqual((a.returncode, b.returncode), (esperado, esperado), nome + a.stderr + b.stderr)

    def test_witness_renamed_to_R_plus_3_fails_in_both_when_the_claim_parameters_are_passed(self):
        with tempfile.TemporaryDirectory() as d:
            renamed = os.path.join(d, "q5_n9_R8_M50.txt")  # o ataque: mesmo código, nome de outra instância
            with open(SMALL) as src, open(renamed, "w") as dst:
                dst.write(src.read())
            a, b = self.both(["--q", "5", "--n", "9", "--R", "5", "--M", "50"], path=renamed)
            self.assertEqual((a.returncode, b.returncode), (2, 2), a.stderr + b.stderr)
            a, b = self.both(["--q", "5", "--n", "9", "--R", "8", "--M", "50"], path=SMALL)  # e o inverso: nome R5, parâmetro R8
            self.assertEqual((a.returncode, b.returncode), (2, 2), a.stderr + b.stderr)

    def test_usage_errors_exit_3_in_both_never_1_or_2(self):
        # 1 e 2 são os `fail_exit_codes` da campanha: um crash ou uso errado não pode virar veredito FAIL
        for args in (["--q", "5", "--n", "9", "--R", "5"], ["--bogus"], ["--q", "x", "--n", "9", "--R", "5", "--M", "50"], ["-q", "5", "--n", "9", "--R", "5", "--M", "50"]):
            with self.subTest(args=args):
                a, b = self.both(args)
                self.assertEqual((a.returncode, b.returncode), (3, 3), a.stderr + b.stderr)
        a = subprocess.run([sys.executable, PY, "--q", "5", "--n", "9", "--R", "5", "--M", "50", "/nao/existe.txt"], capture_output=True, text=True)
        self.assertEqual(a.returncode, 3, a.stderr)

    def test_both_verifiers_print_the_same_sha256_in_explicit_mode(self):
        a, b = self.both(["--q", "5", "--n", "9", "--R", "5", "--M", "50"])
        self.assertEqual((a.returncode, b.returncode), (0, 0))
        self.assertEqual(field(a.stdout, "sha256"), field(b.stdout, "sha256"))
        self.assertEqual((field(a.stdout, "params"), field(b.stdout, "params")), ("explicit", "explicit"))


if __name__ == "__main__":
    unittest.main()
