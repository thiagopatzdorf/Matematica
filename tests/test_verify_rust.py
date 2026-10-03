"""Testes do verificador independente tools/verify-rust (Rust, so std).

Parametros dos witnesses sao lidos do NOME do arquivo pelo TESTE e passados
explicitamente; a ferramenta nunca os deduz do nome.
"""
import glob
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRATE = os.path.join(ROOT, "tools", "verify-rust")
CARGO = shutil.which("cargo") or os.path.expanduser("~/.cargo/bin/cargo")
BIN = os.path.join(CRATE, "target", "release", "verify-rust")
NAME = re.compile(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$")

# K_2(6,1) = 12 (busca local; verificado pelo proprio verify-rust e por contagem de bolas)
K2_6_1 = ["000001", "000111", "001010", "010100", "011100", "011101",
          "100101", "101000", "101110", "110010", "110011", "111011"]


def run(q, n, r, m, path):
    return subprocess.run([BIN, "--q", str(q), "--n", str(n), "--R", str(r), "--M", str(m), path],
                          capture_output=True, text=True).returncode


class VerifyRust(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CARGO):
            raise unittest.SkipTest("cargo ausente: nao da para compilar tools/verify-rust")
        p = subprocess.run([CARGO, "build", "--release", "--offline", "-q"], cwd=CRATE,
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError("cargo build falhou:\n" + p.stderr)
        cls.tmp = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def write(self, name, lines, nl="\n"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", newline="") as f:
            f.write(nl.join(lines) + nl)
        return path

    def witnesses(self):
        out = []
        for f in sorted(glob.glob(os.path.join(ROOT, "data", "codes", "*.txt"))):
            m = NAME.search(f)
            if m:
                out.append((f, *map(int, m.groups())))
        self.assertTrue(out, "nenhum witness em data/codes")
        return out

    def test_witness_valido_nao_e_aceito_com_os_parametros_do_nome(self):
        for f, q, n, r, m in self.witnesses():
            with self.subTest(f=os.path.basename(f)):
                self.assertEqual(run(q, n, r, m, f), 0)

    def test_witness_com_raio_menor_ou_parametros_errados_nao_pode_passar(self):
        # R-1 num witness: nao pode dar 0. (Observado: 1 para todos.)
        for f, q, n, r, m in self.witnesses():
            with self.subTest(f=os.path.basename(f), caso="R-1"):
                self.assertIn(run(q, n, r - 1, m, f), (1, 2))
        f, q, n, r, m = self.witnesses()[0]
        with self.subTest(caso="M errado"):
            self.assertEqual(run(q, n, r, m + 1, f), 2)
        with self.subTest(caso="n errado"):
            self.assertEqual(run(q, n + 1, r, m, f), 2)
        with self.subTest(caso="q menor que um digito usado"):
            self.assertEqual(run(2, n, r, m, f), 2)

    def test_remover_palavra_de_codigo_minimo_deixa_ponto_descoberto(self):
        full = self.write("rep.txt", ["000", "111"])
        self.assertEqual(run(2, 3, 1, 2, full), 0)
        less = self.write("rep1.txt", ["000"])
        self.assertEqual(run(2, 3, 1, 1, less), 1)

    def test_k2_6_1_com_12_palavras_tem_de_passar_e_sem_uma_falhar_cobertura(self):
        p = self.write("k.txt", K2_6_1)
        self.assertEqual(run(2, 6, 1, 12, p), 0)
        # K_2(6,1)=12 e otimo: nenhuma de 11 palavras cobre; tira cada uma.
        for i in range(12):
            q = self.write("k11.txt", K2_6_1[:i] + K2_6_1[i + 1:])
            self.assertEqual(run(2, 6, 1, 11, q), 1, f"sem a palavra {i} deveria descobrir")

    def test_palavra_duplicada_nao_e_rejeitada_com_exit_2(self):
        p = self.write("dup.txt", ["000", "111", "111"])
        self.assertEqual(run(2, 3, 1, 2, p), 2)
        self.assertEqual(run(2, 3, 1, 3, p), 2)

    def test_digito_fora_do_alfabeto_nao_e_rejeitado_com_exit_2(self):
        self.assertEqual(run(2, 3, 1, 2, self.write("d.txt", ["000", "112"])), 2)
        self.assertEqual(run(2, 3, 1, 2, self.write("l.txt", ["000", "11a"])), 2)

    def test_comprimento_errado_nao_e_rejeitado_com_exit_2(self):
        self.assertEqual(run(2, 3, 1, 2, self.write("c.txt", ["000", "1111"])), 2)

    def test_fim_de_linha_crlf_e_aceito(self):
        self.assertEqual(run(2, 3, 1, 2, self.write("crlf.txt", ["000", "111"], nl="\r\n")), 0)

    def test_arquivo_ausente_ou_parametros_faltando_nao_da_exit_3(self):
        self.assertEqual(run(2, 3, 1, 2, os.path.join(self.tmp, "nao_existe.txt")), 3)
        p = self.write("ok.txt", ["000", "111"])
        for args in ([p], ["--q", "2", "--n", "3", "--R", "1", p],
                     ["--q", "2", "--n", "3", "--R", "1", "--M", "2"],
                     ["--q", "x", "--n", "3", "--R", "1", "--M", "2", p],
                     ["--q", "11", "--n", "3", "--R", "1", "--M", "2", p]):
            with self.subTest(args=args):
                self.assertEqual(subprocess.run([BIN] + args, capture_output=True).returncode, 3)

    def test_nome_do_arquivo_nunca_vira_parametro(self):
        # arquivo com nome de q7... mas conteudo binario: so vale o que a CLI diz.
        p = self.write("q7_n9_R4_M1351.txt", ["000", "111"])
        self.assertEqual(run(2, 3, 1, 2, p), 0)


if __name__ == "__main__":
    unittest.main()
