"""Testes do verificador clean-room (Go, BFS multi-fonte em H(n,q))."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "verify-cleanroom")
CODES = os.path.join(ROOT, "data", "codes")
ARTIFACT = os.path.join(ROOT, "campaigns", "covering-codes", "artifacts", "q2_n6_R1_M12.txt")
GO = shutil.which("go") or ("/usr/local/go/bin/go" if os.path.exists("/usr/local/go/bin/go") else None)
NAME = re.compile(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$")


def words(path):
    with open(path) as f:
        return [l.strip() for l in f if l.strip()]


@unittest.skipUnless(GO, "toolchain Go ausente: teste do verificador clean-room pulado")
class CleanRoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="cleanroom_")
        cls.bin = os.path.join(cls.tmp, "verify-cleanroom")
        env = dict(os.environ, GOFLAGS="-mod=mod", GOCACHE=os.path.join(cls.tmp, "gocache"))
        r = subprocess.run([GO, "build", "-o", cls.bin, "."], cwd=SRC, env=env,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("falha ao compilar: " + r.stderr)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_v(self, path, q, n, R, M, drop=()):
        args = [self.bin]
        for k, v in (("--q", q), ("--n", n), ("--R", R), ("--M", M)):
            if k not in drop:
                args += [k, str(v)]
        args.append(path)
        r = subprocess.run(args, capture_output=True, text=True)
        return r.returncode, r.stdout

    def write(self, lines, name="w.txt"):
        p = os.path.join(self.tmp, name)
        with open(p, "w") as f:
            f.write("".join(l + "\n" for l in lines))
        return p

    def params(self, fn):
        return tuple(int(x) for x in NAME.search(fn).groups())

    def codes(self):
        fs = sorted(f for f in os.listdir(CODES) if NAME.search(f))
        self.assertGreaterEqual(len(fs), 10)  # a pasta cresce (v0.5 trouxe 1137 e 1141); não fixar a contagem
        return fs

    def test_dez_witnesses_cobrem_com_parametros_do_nome_passados_explicitamente(self):
        for fn in self.codes():
            q, n, R, M = self.params(fn)
            code, out = self.run_v(os.path.join(CODES, fn), q, n, R, M)
            self.assertEqual(code, 0, (fn, out))

    def test_raio_menor_que_o_certificado_deixa_ponto_descoberto(self):
        # q7_n9 e q5_n10 sao lentos; basta cobrir todos (cada um ~ segundos)
        for fn in self.codes():
            q, n, R, M = self.params(fn)
            code, out = self.run_v(os.path.join(CODES, fn), q, n, R - 1, M)
            self.assertEqual(code, 1, (fn, out))
            self.assertIn("first_uncovered=", out)

    def test_parametros_q_n_M_errados_dao_2(self):
        fn = "q5_n7_R2_M500.txt"
        p = os.path.join(CODES, fn)
        # q maior que o real nao contradiz o conteudo (digitos < 5 < 6): so muda o espaco
        self.assertEqual(self.run_v(p, 6, 7, 2, 500)[0], 1)
        for kw in (dict(q=4), dict(n=8), dict(n=6), dict(M=499), dict(M=501)):
            a = dict(q=5, n=7, R=2, M=500)
            a.update(kw)
            code, out = self.run_v(p, **a)
            self.assertEqual(code, 2, (kw, out))

    def test_duplicata_digito_invalido_e_comprimento_errado_dao_2(self):
        base = ["000", "111"]
        self.assertEqual(self.run_v(self.write(["000", "000"]), 2, 3, 1, 2)[0], 2)
        self.assertEqual(self.run_v(self.write(["000", "000"]), 2, 3, 1, 1)[0], 2)
        self.assertEqual(self.run_v(self.write(["000", "112"]), 2, 3, 1, 2)[0], 2)
        self.assertEqual(self.run_v(self.write(["000", "11"]), 2, 3, 1, 2)[0], 2)
        self.assertEqual(self.run_v(self.write(["000", "1111"]), 2, 3, 1, 2)[0], 2)
        self.assertEqual(self.run_v(self.write(["000", "11a"]), 2, 3, 1, 2)[0], 2)
        self.assertEqual(self.run_v(self.write(base), 2, 3, 1, 2)[0], 0)

    def test_codigo_de_repeticao_sem_uma_palavra_nao_cobre(self):
        self.assertEqual(self.run_v(self.write(["000", "111"]), 2, 3, 1, 2)[0], 0)
        self.assertEqual(self.run_v(self.write(["000"]), 2, 3, 1, 1)[0], 1)
        self.assertEqual(self.run_v(self.write(["111"]), 2, 3, 1, 1)[0], 1)

    def test_erros_operacionais_dao_3(self):
        p = self.write(["000", "111"])
        self.assertEqual(self.run_v(os.path.join(self.tmp, "nao_existe.txt"), 2, 3, 1, 2)[0], 3)
        for k in ("--q", "--n", "--R", "--M"):
            self.assertEqual(self.run_v(p, 2, 3, 1, 2, drop=(k,))[0], 3, k)
        self.assertEqual(self.run_v(p, 1, 3, 1, 2)[0], 3)
        self.assertEqual(self.run_v(p, 11, 3, 1, 2)[0], 3)
        self.assertEqual(self.run_v(p, 2, 3, 1, 0)[0], 3)

    def test_nome_do_arquivo_nunca_fornece_parametro(self):
        src = os.path.join(CODES, "q5_n7_R2_M500.txt")
        dst = os.path.join(self.tmp, "q9_n9_R9_M9.txt")
        shutil.copy(src, dst)
        self.assertEqual(self.run_v(dst, 5, 7, 2, 500)[0], 0)
        self.assertEqual(self.run_v(dst, 9, 9, 9, 9)[0], 2)

    @unittest.skipUnless(os.path.exists(ARTIFACT), "artefato K_2(6,1)=12 ausente")
    def test_K2_6_1_igual_12_cobre_e_toda_remocao_deixa_de_cobrir(self):
        w = words(ARTIFACT)
        self.assertEqual(len(w), 12)
        self.assertEqual(self.run_v(self.write(w), 2, 6, 1, 12)[0], 0)
        for i in range(12):
            sub = w[:i] + w[i + 1:]
            self.assertEqual(self.run_v(self.write(sub), 2, 6, 1, 11)[0], 1, i)


if __name__ == "__main__":
    unittest.main()
