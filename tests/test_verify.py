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


class ExplicitParametersTest(unittest.TestCase):
    """Modo explícito (--q --n --R --M): o verificador confere os parâmetros contra o conteúdo e contra o nome do arquivo.

    Contexto (red team D-12): lendo q, n, R, M só do NOME do arquivo, o mesmo código renomeado com R+3 passava. Contrato de saída:
    0 cobre; 1 descoberto; 2 o witness contradiz os parâmetros; 3 uso incorreto/operacional (nunca confundido com 1/2).
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.bin = os.path.join(cls.tmp, "verify")
        cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc")
        subprocess.run([cc, "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", cls.bin,
                        os.path.join(ROOT, "tools/verify/verify.c")], check=True)
        cls.path = os.path.join(ROOT, "data/codes/q5_n9_R5_M50.txt")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def run_(self, *args, path=None, stdin=None):
        return subprocess.run([self.bin, *args, path or self.path], input=stdin, capture_output=True, text=True)

    def test_explicit_parameters_that_match_the_witness_pass_and_report_the_same_sha256(self):
        for path in CODES:
            q, n, R, M = params(path)
            with self.subTest(code=os.path.basename(path)):
                r = subprocess.run([self.bin, "--q", str(q), "--n", str(n), "--R", str(R), "--M", str(M), path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("params=explicit", r.stdout)
                self.assertEqual(VerifierTest.field(r.stdout, "sha256"), canon(lines_of(path)))

    def test_same_code_with_R_plus_3_in_the_file_name_fails_when_the_claim_says_R(self):
        # o ataque do red team: renomear o witness para outra instância. Agora o nome contradiz os parâmetros entregues.
        renamed = os.path.join(self.tmp, "q5_n9_R8_M50.txt")
        shutil.copy(self.path, renamed)
        r = self.run_("--q", "5", "--n", "9", "--R", "5", "--M", "50", path=renamed)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("contradizem o nome", r.stderr)

    def test_explicit_R_plus_3_on_a_file_named_for_R_fails(self):
        r = self.run_("--q", "5", "--n", "9", "--R", "8", "--M", "50")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_explicit_M_minus_1_and_M_plus_1_fail_because_the_word_count_differs(self):
        # nome sem o padrão (stdin): só o conteúdo pode contradizer o M
        data = "\n".join(lines_of(self.path)) + "\n"
        for M in ("49", "51"):
            with self.subTest(M=M):
                r = subprocess.run([self.bin, "--q", "5", "--n", "9", "--R", "5", "--M", M, "-"], input=data, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("M esperado", r.stderr)

    def test_explicit_n_and_q_that_contradict_the_words_fail(self):
        data = "\n".join(lines_of(self.path)) + "\n"
        for opts, msg in ((("--q", "5", "--n", "8"), "comprimento"), (("--q", "4", "--n", "9"), "dígito >= q")):
            with self.subTest(opts=opts):
                r = subprocess.run([self.bin, *opts, "--R", "5", "--M", "50", "-"], input=data, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn(msg, r.stderr)

    def test_explicit_R_too_small_is_an_uncovered_failure_exit_1(self):
        data = "\n".join(lines_of(self.path)) + "\n"
        r = subprocess.run([self.bin, "--q", "5", "--n", "9", "--R", "2", "--M", "50", "-"], input=data, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertGreater(int(VerifierTest.field(r.stdout, "uncovered")), 0)

    def test_explicit_mode_requires_all_four_and_never_falls_back_to_the_name(self):
        for faltando in ("--q", "--n", "--R", "--M"):
            args = [x for k, v in (("--q", "5"), ("--n", "9"), ("--R", "5"), ("--M", "50")) if k != faltando for x in (k, v)]
            with self.subTest(faltando=faltando):
                r = self.run_(*args)
                self.assertEqual(r.returncode, 3, r.stdout + r.stderr)

    def test_usage_errors_exit_3_so_they_are_never_read_as_a_fail_verdict(self):
        casos = {"opção desconhecida": ("--bogus", "1"), "valor não inteiro": ("--q", "cinco", "--n", "9", "--R", "5", "--M", "50"),
                 "mistura legado+explícito": ("-q", "5", "--n", "9", "--R", "5", "--M", "50", "--q", "5")}
        for nome, args in casos.items():
            with self.subTest(caso=nome):
                self.assertEqual(self.run_(*args).returncode, 3)
        self.assertEqual(subprocess.run([self.bin, "--q", "5", "--n", "9", "--R", "5", "--M", "50", "/nao/existe.txt"], capture_output=True, text=True).returncode, 3)

    def test_legacy_mode_still_reads_the_name_and_says_so(self):
        r = subprocess.run([self.bin, self.path], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("params=legacy", r.stdout)


if __name__ == "__main__":
    unittest.main()
