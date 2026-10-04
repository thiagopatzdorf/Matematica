"""Avaliador `ponte_ledger`: o ledger, os arquivos de `data/codes` e os teoremas Lean contam a mesma história?

Para cada célula com `ours_lean` em `ledger/cells.json`, confere:
  1. `M` do ledger == `M` do nome do arquivo (q<Q>_n<N>_R<R>_M<M>.txt) == número de palavras do arquivo;
  2. q, n, R do nome do arquivo == os da célula;
  3. o sha256 (do ARQUIVO) registrado no ledger == o do arquivo em disco;
  4. a declaração citada existe nos .lean (nome completo, com `namespace`, comentários ignorados);
  5. os números embutidos no nome da declaração (K7_9_4_le_1134_...) batem com a célula e com M.
Célula sem arquivo (ex.: K2(6,1), cujo código vive nos G610_Chunk_*) pula 1–3 e é listada em `puladas`.
Divergência é ACHADO: este avaliador nunca corrige número nenhum.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .base import RAIZ, Avaliador, registrar, relativo, sha256_arquivo
from .lean_honesty import arquivos_lean, declaracoes, limpar_lean

_NOME = re.compile(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$")
_DECL_NUMS = re.compile(r"K_?(\d+)_(\d+)_(\d+)_(?:le|eq)_?(\d+)")


def _palavras(caminho: Path) -> int:
    return sum(1 for ln in caminho.read_text().splitlines() if ln.strip())


@registrar
class PonteLedger(Avaliador):
    id = "ponte_ledger"
    versao = "1"
    descricao = "ledger × data/codes × declarações Lean: M, nome do arquivo, nº de palavras, sha256 e declaração existem e batem"
    alvo_padrao = str(RAIZ / "ledger" / "cells.json")

    def avaliar(self, alvo, **opcoes):
        alvo = Path(alvo)
        raiz = Path(opcoes.get("raiz") or RAIZ)
        repro = f"python3 -m evaluators {self.id} {relativo(alvo)} --json"
        if not alvo.is_file():
            return self.falha_de_ambiente(f"ledger não existe: {alvo}", "alvo_ausente", comando_reproducao=repro)
        celulas = json.loads(alvo.read_text(encoding="utf-8"))["cells"]
        lean_dir = Path(opcoes.get("lean") or raiz / "CoveringLean")
        if not lean_dir.is_dir():
            return self.falha_de_ambiente(f"sem {lean_dir}", "alvo_ausente", comando_reproducao=repro)
        decls: set[str] = set()
        for arq in arquivos_lean(lean_dir):
            decls |= declaracoes(limpar_lean(arq.read_text(encoding="utf-8", errors="replace")))

        achados: list[dict] = []
        puladas: list[dict] = []
        conferidas = 0

        def achar(cid, checagem, detalhe, **extra):
            achados.append({"celula": cid, "checagem": checagem, "detalhe": detalhe, **extra})

        for c in celulas:
            o = c.get("ours_lean")
            if not o:
                continue
            conferidas += 1
            cid, M = c["id"], o["M"]
            decl = o.get("declaration") or ""
            if decl not in decls:
                achar(cid, "declaracao_existe", f"{decl!r} não é declarada em {relativo(lean_dir, raiz)}")
            nums = _DECL_NUMS.search(decl.rsplit(".", 1)[-1])
            if nums:
                q, n, r, m = map(int, nums.groups())
                if (q, n, r) != (c["q"], c["n"], c["R"]):
                    achar(cid, "declaracao_vs_celula", f"{decl} fala de K{q}({n},{r}), a célula é K{c['q']}({c['n']},{c['R']})")
                if m != M:
                    achar(cid, "declaracao_vs_M", f"{decl} fala de {m}, o ledger diz M={M}", ledger=M, declaracao=m)
            arq = o.get("file")
            if not arq:
                puladas.append({"celula": cid, "motivo": "ledger não aponta arquivo em data/codes (código fora de data/codes)"})
                continue
            p = raiz / arq
            if not p.is_file():
                achar(cid, "arquivo_existe", f"{arq} não existe")
                continue
            nm = _NOME.search(p.name)
            if not nm:
                achar(cid, "nome_do_arquivo", f"{p.name} fora do padrão q<Q>_n<N>_R<R>_M<M>.txt")
                continue
            q, n, r, m_nome = map(int, nm.groups())
            if (q, n, r) != (c["q"], c["n"], c["R"]):
                achar(cid, "arquivo_vs_celula", f"{p.name} é K{q}({n},{r}), a célula é K{c['q']}({c['n']},{c['R']})")
            palavras = _palavras(p)
            if not (M == m_nome == palavras):
                achar(cid, "M_ledger_nome_palavras", f"ledger M={M}, nome do arquivo M={m_nome}, palavras no arquivo={palavras}",
                      ledger=M, nome=m_nome, palavras=palavras, arquivo=arq)
            if o.get("sha256") and o["sha256"] != sha256_arquivo(p):
                achar(cid, "sha256_arquivo", f"sha256 do ledger != sha256 do arquivo {arq}", arquivo=arq)
        citados = {Path(c["ours_lean"]["file"]).name for c in celulas if c.get("ours_lean") and c["ours_lean"].get("file")}
        sem_ledger = sorted(p.name for p in (raiz / "data" / "codes").glob("*.txt") if p.name not in citados)
        evid = {"celulas_conferidas": conferidas, "codigos_fora_do_ledger_ours_lean": sem_ledger,
                "declaracoes_lean_indexadas": len(decls), "achados": achados, "n_achados": len(achados), "puladas": puladas}
        if achados:
            a = achados[0]
            return self.resultado(False, f"{len(achados)} divergência(s); primeira: {a['celula']} ({a['checagem']}): {a['detalhe']}",
                                  evidencia=evid, sha256_arquivo=sha256_arquivo(alvo), comando_reproducao=repro)
        return self.resultado(True, f"{conferidas} células ours_lean conferidas ({len(puladas)} sem arquivo), sem divergência",
                              evidencia=evid, sha256_arquivo=sha256_arquivo(alvo), comando_reproducao=repro)
