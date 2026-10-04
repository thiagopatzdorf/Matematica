"""Avaliador `covering_code`: o código cobre Z_q^n com raio R? Exato, via tools/verify/verify.c.

Compila o verificador sob demanda num diretório temporário (ou usa EVALUATORS_VERIFY_BIN, um binário
já compilado) e, quando o código não cobre, devolve pontos descobertos concretos em `evidencia`.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import RAIZ, Avaliador, registrar, relativo, sha256_arquivo

FONTE_C = RAIZ / "tools" / "verify" / "verify.c"
PONTOS_PADRAO = 10


def _compilador() -> str | None:
    return os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")


def _campos(linha: str) -> dict:
    return dict(re.findall(r"(\w+)=(\S+)", linha))


@registrar
class CoveringCode(Avaliador):
    id = "covering_code"
    versao = "1"
    descricao = "código de cobertura K_q(n,R) ≤ M cobre todo ponto? (verificador exato em C; lista pontos descobertos)"

    def avaliar(self, alvo, **opcoes):
        caminho = Path(alvo)
        pontos = int(opcoes.get("pontos", PONTOS_PADRAO))
        cmd_repro = f"python3 -m evaluators {self.id} {relativo(caminho)} --json"
        if not caminho.is_file():
            return self.falha_de_ambiente(f"arquivo não existe: {alvo}", "alvo_ausente", comando_reproducao=cmd_repro)
        sha_arq = sha256_arquivo(caminho)
        with tempfile.TemporaryDirectory(prefix="verify-") as tmp:
            binario = os.environ.get("EVALUATORS_VERIFY_BIN")
            if not binario:
                cc = _compilador()
                if not cc:
                    return self.falha_de_ambiente(
                        "sem compilador C (cc/gcc/clang): instale um, defina CC, ou aponte EVALUATORS_VERIFY_BIN "
                        "para um verify já compilado", "sem_compilador", sha256_arquivo=sha_arq,
                        comando_reproducao=cmd_repro)
                binario = os.path.join(tmp, "verify")
                b = subprocess.run([cc, "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", binario, str(FONTE_C)],
                                   capture_output=True, text=True)
                if b.returncode != 0:
                    return self.falha_de_ambiente("verify.c não compilou: " + b.stderr.strip()[-300:],
                                                  "compilacao_falhou", sha256_arquivo=sha_arq,
                                                  comando_reproducao=cmd_repro)
            args = [binario]
            for chave, flag in (("q", "-q"), ("n", "-n"), ("r", "-r"), ("m", "-m")):
                if chave in opcoes:
                    args += [flag, str(opcoes[chave])]
            args += ["-u", str(pontos), str(caminho)]
            try:
                p = subprocess.run(args, capture_output=True, text=True,
                                   timeout=float(opcoes.get("tempo_limite_s", 600)))
            except subprocess.TimeoutExpired:
                return self.falha_de_ambiente("verificador passou do tempo limite", "tempo_limite",
                                              sha256_arquivo=sha_arq, comando_reproducao=cmd_repro)
        linhas = p.stdout.splitlines()
        resumo = _campos(linhas[0]) if linhas else {}
        evid = {"codigo_de_saida": p.returncode,
                "comando_c": " ".join(["tools/verify/verify", *args[1:-1], relativo(caminho)])}
        if p.returncode == 2 or "uncovered" not in resumo:
            msg = (p.stderr.strip() or p.stdout.strip() or "sem saída").splitlines()[-1]
            evid["erro_do_verificador"] = msg
            return self.resultado(False, f"formato inválido: {msg}", evidencia=evid, sha256_arquivo=sha_arq,
                                  comando_reproducao=cmd_repro)
        for k in ("q", "n", "R", "M", "points", "uncovered"):
            evid[k] = int(resumo[k])
        livres = [ln.split("=", 1)[1] for ln in linhas[1:] if ln.startswith("uncovered_point=")]
        evid["pontos_descobertos"] = livres
        evid["pontos_descobertos_listados"] = len(livres)
        ok = p.returncode == 0 and evid["uncovered"] == 0
        if ok:
            veredito = f"cobre: 0 pontos descobertos de {evid['points']} (M={evid['M']}, q={evid['q']} n={evid['n']} R={evid['R']})"
        else:
            veredito = (f"NÃO cobre: {evid['uncovered']} pontos descobertos de {evid['points']} "
                        f"(ex.: {livres[0] if livres else '?'})")
        return self.resultado(ok, veredito, evidencia=evid, sha256_arquivo=sha_arq,
                              sha256_canonico=resumo.get("sha256"), comando_reproducao=cmd_repro)
