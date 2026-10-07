"""Cruzamento estrutural entre o release openai/math e as frentes deste repositório.

Três passos, todos reproduzíveis:
  1. `ler_contents` + `ler_disciplinas`: o mapa CONTENTS.md e o overview.tex do release viram uma lista
     de famílias (número, título, resumo, disciplina, manuscritos com caminho e resumo).
  2. Embeddings (fastembed, CPU) de cada família, cada manuscrito, cada frente nossa e cada etiqueta do
     vocabulário de estruturas. `etiquetas` padroniza a similaridade por etiqueta (z sobre todas as
     unidades), então "parece com códigos de cobertura" significa "mais do que a média do corpus".
  3. `pontuar_pares`: nota = 0,5·cos(texto, frente) + 0,5·cos(perfil de etiquetas, perfil da frente).
     A segunda metade é o que dá o cruzamento por ESTRUTURA: dois textos sem palavra em comum casam se
     ativam as mesmas etiquetas.

Uso (precisa de `pip install fastembed numpy` e de um checkout do release na revisão desejada):
    python3 tools/literatura/cruzamento_openai_math.py <CONTENTS.md> <overview.tex> \
        docs/literatura/cruzamento-openai-math/frentes.json \
        docs/literatura/cruzamento-openai-math/vocabulario.json saida.json [modelo]

O resultado é triagem: a relação de verdade só se afirma depois de ler a fonte (o doc diz quais li).
"""
from __future__ import annotations

import html
import json
import re
import sys

import numpy as np

_CELULA = re.compile(r"<td>\n(.*?)\n</td>", re.S)
_FAMILIA = re.compile(r"\*\*(\d{3})\. (.*?)\*\*\s*(.*)", re.S)
_MANUSCRITO = re.compile(r"&emsp;\[(.*?)\]\((.*?)\)\s*(.*)", re.S)
_LEAN = re.compile(r"\(\[Lean\]\(.*?\)\)")


def _limpa(s: str) -> str:
    s = _LEAN.sub("", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def ler_contents(texto: str) -> list[dict]:
    """Famílias do CONTENTS.md, cada uma com os manuscritos que vêm logo abaixo dela."""
    familias: list[dict] = []
    for celula in _CELULA.findall(texto):
        celula = celula.strip()
        m = _FAMILIA.match(celula)
        if m:
            familias.append({"familia": m.group(1), "titulo": _limpa(m.group(2)),
                             "resumo": _limpa(m.group(3)), "manuscritos": []})
            continue
        m = _MANUSCRITO.match(celula)
        if m:
            if not familias:
                raise ValueError("manuscrito antes de qualquer família: o formato do CONTENTS.md mudou")
            familias[-1]["manuscritos"].append({"titulo": _limpa(m.group(1)), "caminho": m.group(2),
                                                "resumo": _limpa(m.group(3))})
    return familias


def ler_disciplinas(tex: str) -> dict[str, str]:
    """Família -> disciplina, pela seção do overview.tex em que o \\resultentry aparece."""
    disc, secao = {}, None
    for linha in tex.splitlines():
        m = re.match(r"\\cataloguesection\{(.*?)\}", linha)
        if m:
            secao = m.group(1)
        m = re.match(r"\\resultentry\{(\d{3})\}", linha)
        if m and secao:
            disc[m.group(1)] = secao
    return disc


def _normaliza(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)


def etiquetas(U: np.ndarray, T: np.ndarray) -> np.ndarray:
    """z-score por etiqueta da similaridade unidade×etiqueta (linhas de U e T já normalizadas)."""
    S = U @ T.T
    return (S - S.mean(0)) / (S.std(0) + 1e-12)


def pontuar_pares(U: np.ndarray, Z: np.ndarray, deles: list[int], nossos: list[int]) -> np.ndarray:
    """Matriz len(deles)×len(nossos) com 0,5·cos direto + 0,5·cos dos perfis positivos de etiqueta."""
    P = _normaliza(np.clip(Z, 0, None))
    direto = U[deles] @ U[nossos].T
    estrutura = P[deles] @ P[nossos].T
    return 0.5 * direto + 0.5 * estrutura


def melhores_por_familia(notas: np.ndarray, ids_deles: list[str], ids_nossos: list[str], k: int) -> list[dict]:
    """Os k pares (família, frente) mais fortes; uma família conta pelo seu manuscrito mais forte."""
    melhor: dict[tuple[str, str], tuple[float, str]] = {}
    for i, uid in enumerate(ids_deles):
        fam = uid.split(".")[0]
        for j, fr in enumerate(ids_nossos):
            n = float(notas[i, j])
            if n > melhor.get((fam, fr), (-9.0, ""))[0]:
                melhor[(fam, fr)] = (n, uid)
    ordem = sorted(melhor.items(), key=lambda kv: -kv[1][0])[:k]
    return [{"familia": f, "frente": fr, "nota": round(n, 4), "unidade": u} for (f, fr), (n, u) in ordem]


def por_frente(notas: np.ndarray, ids_deles: list[str], ids_nossos: list[str], k: int) -> dict[str, list[dict]]:
    """Para cada frente, as k famílias com maior z DENTRO da coluna da frente.

    Por que existe: a nota bruta favorece frentes de vocabulário genérico (complexidade, LP), e o ranking
    global enterra a melhor família de uma frente específica. O z por coluna compara cada família só com
    as outras famílias diante da mesma frente.
    """
    fams = sorted({u.split(".")[0] for u in ids_deles})
    pos = {f: i for i, f in enumerate(fams)}
    M = np.full((len(fams), len(ids_nossos)), -9.0)
    for i, uid in enumerate(ids_deles):
        r = pos[uid.split(".")[0]]
        M[r] = np.maximum(M[r], notas[i])
    Zc = (M - M.mean(0)) / (M.std(0) + 1e-12)
    saida = {}
    for j, fr in enumerate(ids_nossos):
        ordem = np.argsort(-Zc[:, j])[:k]
        saida[fr] = [{"familia": fams[r], "nota": round(float(M[r, j]), 4), "z": round(float(Zc[r, j]), 2)} for r in ordem]
    return saida


def main(argv: list[str]) -> None:
    from fastembed import TextEmbedding  # só aqui: o resto do módulo roda sem ela

    contents, tex, frentes_p, vocab_p, saida = argv[:5]
    modelo = argv[5] if len(argv) > 5 else "BAAI/bge-base-en-v1.5"
    fams = ler_contents(open(contents, encoding="utf-8").read())
    disc = ler_disciplinas(open(tex, encoding="utf-8").read())
    frentes = json.load(open(frentes_p, encoding="utf-8"))
    voc = json.load(open(vocab_p, encoding="utf-8"))
    unidades = []
    for f in fams:
        unidades.append((f["familia"], f"{f['titulo']} {f['resumo']}"))
        unidades += [(f"{f['familia']}.{i}", f"{m['titulo']}. {m['resumo']}") for i, m in enumerate(f["manuscritos"])]
    n_deles = len(unidades)
    unidades += [(x["id"], x["texto"]) for x in frentes]
    emb = TextEmbedding(modelo)
    U = _normaliza(np.array(list(emb.embed([t for _, t in unidades], batch_size=16)), dtype=np.float32))
    tags = list(voc)
    T = _normaliza(np.array(list(emb.embed([voc[t] for t in tags])), dtype=np.float32))
    Z = etiquetas(U, T)
    deles, nossos = list(range(n_deles)), list(range(n_deles, len(unidades)))
    notas = pontuar_pares(U, Z, deles, nossos)
    perfil = {uid: [[tags[j], round(float(Z[i, j]), 2)] for j in np.argsort(-Z[i])[:4] if Z[i, j] > 1.0]
              for i, (uid, _) in enumerate(unidades)}
    json.dump({"modelo": modelo, "etiquetas": tags,
               "familias": [{"familia": f["familia"], "titulo": f["titulo"], "disciplina": disc.get(f["familia"]),
                             "n_manuscritos": len(f["manuscritos"]), "perfil": perfil[f["familia"]]} for f in fams],
               "frentes": [{"id": x["id"], "perfil": perfil[x["id"]]} for x in frentes],
               "pares": melhores_por_familia(notas, [u for u, _ in unidades[:n_deles]], [x["id"] for x in frentes], 150),
               "por_frente": por_frente(notas, [u for u, _ in unidades[:n_deles]], [x["id"] for x in frentes], 10)},
              open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
