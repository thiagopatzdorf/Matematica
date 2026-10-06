#!/usr/bin/env python3
"""Códigos lineares sistemáticos como célula base do lote (tools/certificar/gerar.py).

As tabelas do Kéri derivam várias cotas superiores de um código linear, sem arquivo de código:
"Hamming code", "perfect code" (Golay), "linear code". Um código linear `[n, k]_q` com raio de
cobertura `R` dá `K_q(n, R) ≤ q^k`, e o kernel do Lean confere isso barato (`Syn.lin_cert`,
CoveringLean/SynLinear.lean): `k²` dígitos do bloco identidade e `q^(n-k)` pontos do
transversal, em vez dos `q^n · q^k` pares de um witness explícito.

Cada código mora em tools/certificar/lineares/K<q>_<n>_<R>_M<M>.json:

    {"q": 2, "n": 23, "R": 3, "gerador": [[1, 0, ..., 0, p...], ...],   # k linhas, G = [I_k | P]
     "construcao": "código de Golay binário [23,12]", "chave_keri": "h"}

Dois verificadores, independentes um do outro:

* `cobre_por_sindromes`: H = [-Pᵀ | I_r]; o código cobre com raio R se as síndromes dos vetores
  de peso ≤ R esgotam Z_q^r (o avaliador Python, rodado em tests/test_certificar.py);
* o kernel do Lean, com as testemunhas do transversal que `testemunhas` calcula aqui.

    python3 tools/certificar/lineares.py --gravar   # (re)grava os JSON das construções abaixo
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.set_int_max_str_digits(0)  # o fluxo de testemunhas é um Nat de dezenas de milhares de dígitos

RAIZ = Path(__file__).resolve().parents[2]
LIN = RAIZ / "tools" / "certificar" / "lineares"
VERIFICADOR = ("avaliador de síndromes em Python (tools/certificar/lineares.py, cobre_por_sindromes), "
               "rodado em tests/test_certificar.py")


def _enc(v, q) -> int:
    return sum(int(d) * q**i for i, d in enumerate(v))


def validar_forma(q: int, n: int, G: list[list[int]]) -> int:
    """Confere G = [I_k | P] com entradas em Z_q; devolve k."""
    k = len(G)
    if k == 0 or k > n or any(len(g) != n or min(g) < 0 or max(g) >= q for g in G):
        raise ValueError("gerador fora de Z_q^n")
    for j in range(k):
        for l in range(k):
            if G[j][l] != (1 if j == l else 0):
                raise ValueError("gerador não é sistemático nas primeiras k coordenadas")
    return k


def cobre_por_sindromes(q: int, n: int, R: int, G: list[list[int]]) -> bool:
    """Avaliador exato pelas síndromes: todo coset tem líder de peso ≤ R."""
    k = validar_forma(q, n, G)
    r = n - k
    cols = [tuple((-G[j][k + i]) % q for i in range(r)) for j in range(k)]
    cols += [tuple(1 if t == i else 0 for t in range(r)) for i in range(r)]
    vistas = {(0,) * r}
    for w in range(1, R + 1):
        for sup in itertools.combinations(range(n), w):
            for vals in itertools.product(range(1, q), repeat=w):
                vistas.add(tuple(sum(v * cols[j][i] for v, j in zip(vals, sup)) % q for i in range(r)))
    return len(vistas) == q**r


def testemunhas(q: int, n: int, R: int, G: list[list[int]]) -> list[int]:
    """Para cada ponto y_t do transversal (nulo nas k primeiras coordenadas, coordenada k+j =
    dígito j de t), a mensagem m (codificada) com d(m·G, y_t) ≤ R. Levanta erro se faltar algum."""
    k = validar_forma(q, n, G)
    r = n - k
    w: list[int | None] = [None] * q**r
    for peso in range(R + 1):
        for sup in itertools.combinations(range(n), peso):
            for vals in itertools.product(range(1, q), repeat=peso):
                e = [0] * n
                for p, v in zip(sup, vals):
                    e[p] = v
                m = [(-e[j]) % q for j in range(k)]
                y = [(e[i] + sum(m[j] * G[j][i] for j in range(k))) % q for i in range(n)]
                t = _enc(y[k:], q)
                if w[t] is None:
                    w[t] = _enc(m, q)
    falta = [t for t, x in enumerate(w) if x is None]
    if falta:
        raise ValueError(f"o código não cobre com raio {R}: {len(falta)} pontos do transversal sem testemunha")
    return w  # type: ignore[return-value]


def ler_lineares() -> dict:
    """{(q,n,R): (M, caminho, G, construcao)}; aborta se algum JSON não cobre."""
    out = {}
    for p in sorted(LIN.glob("K*_M*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        q, n, R, G = d["q"], d["n"], d["R"], d["gerador"]
        k = validar_forma(q, n, G)
        M = q**k
        if p.stem != f"K{q}_{n}_{R}_M{M}":
            raise SystemExit(f"{p.name}: nome não bate com q, n, R e q^k = {M}")
        if not cobre_por_sindromes(q, n, R, G):
            raise SystemExit(f"{p.name}: o código não cobre com raio {R}")
        s = (q, n, R)
        if s not in out or M < out[s][0]:
            out[s] = (M, p, G, d["construcao"])
    return out


CHUNK = 1024  # pontos do transversal por teorema: um `decide +kernel` com 28 561 pontos estourou a memória


def lean(ident: str, q: int, n: int, R: int, G: list[list[int]]) -> tuple[str, str]:
    """(nome do módulo, texto) do certificado Lean `CoveringLedger.Lin.l_<ident> : UB q n R q^k`."""
    k = validar_forma(q, n, G)
    w = testemunhas(q, n, R, G)
    total = len(w)
    B = q**k + 1  # testemunha < q^k; q^k seria a marca de órfão (não há órfão aqui)
    Gs = [_enc(g, q) for g in G]
    P = f"P_{ident}"
    linhas = [
        f"-- GERADO por tools/certificar/gerar.py (lineares.py); não edite à mão. Código linear de {ident}.",
        "import CoveringLean.SynLinear",
        "import CoveringLean.Regras",
        "",
        f"/-! `K_{q}({n},{R}) ≤ {q**k}` por código linear (`Syn.lin_cert`); gerado, não edite à mão. -/",
        "",
        "namespace CoveringLedger.Lin",
        "open CoveringUB Syn",
        "",
        f"/-- [{n},{k}]_{q}, G = [I_{k} | P] (linha j = Σ dígito_i · {q}^i), raio {R}. -/",
        f"def {P} : Syn.Spec where",
        f"  q := {q}", f"  n := {n}", f"  k := {k}", "  o := 0", f"  R := {R}",
        f"  Gs := {Gs}", "  reps := [0]", "  orphs := []", "  PN := 0", "  b := 0", "  cnt := 0",
        "",
    ]
    nch = -(-total // CHUNK)
    for c in range(nch):
        bloco = w[c * CHUNK:(c + 1) * CHUNK]
        N = 0
        for x in reversed(bloco):  # Horner: N = Σ w[t]·B^t sem potências gigantes
            N = N * B + x
        linhas += [f"/-- Testemunhas dos pontos {c * CHUNK}..{c * CHUNK + len(bloco) - 1} do transversal, na base {B}. -/",
                   f"theorem T_{ident}_{c} : chkT {P} {B} {len(bloco)} {c * CHUNK}",
                   f"    {N} = true := by",
                   "  decide +kernel", ""]
    casos = [f"    | {c}, _ => exact fun i _ hlt => chkT_sound {P} _ _ _ _ T_{ident}_{c} i (by omega)"
             for c in range(nch)]
    linhas += [
        "set_option maxRecDepth 100000 in",
        f"theorem hT_{ident} : ∀ t < {total}, ∃ w, okT {P} t w = true :=",
        f"  all_of_chunks (fun t => ∃ w, okT {P} t w = true) {CHUNK} {nch} {total} (by norm_num) (by",
        "    intro c hc",
        "    match c, hc with",
        *casos,
        f"    | c + {nch}, h => exact absurd h (by omega))",
        "",
        "set_option maxRecDepth 100000 in",
        f"theorem l_{ident} : UB {q} {n} {R} {q**k} :=",
        f"  UB.of_exists (Syn.lin_cert {P} rfl rfl rfl (by decide +kernel) ⟨rfl, by decide⟩",
        f"    (by decide +kernel) rfl rfl hT_{ident})",
        "",
        "end CoveringLedger.Lin",
        "",
    ]
    return f"Lin_{ident}", "\n".join(linhas)


# ---------------------------------------------------------------- construções


def _sistematico(q: int, G: list[list[int]]) -> list[list[int]]:
    """Escalona G (q primo) até [I_k | P] nas primeiras k colunas; levanta erro se não der."""
    G = [list(g) for g in G]
    k = len(G)
    for c in range(k):
        piv = next((i for i in range(c, k) if G[i][c] % q), None)
        if piv is None:
            raise ValueError("as primeiras k colunas não são independentes")
        G[c], G[piv] = G[piv], G[c]
        inv = pow(G[c][c], -1, q)
        G[c] = [(x * inv) % q for x in G[c]]
        for i in range(k):
            if i != c and G[i][c]:
                f = G[i][c]
                G[i] = [(a - f * b) % q for a, b in zip(G[i], G[c])]
    return G


def _ciclico(q: int, n: int, g: list[int]) -> list[list[int]]:
    """Gerador do código cíclico de polinômio g (coeficientes do grau 0 ao grau n-k)."""
    k = n - (len(g) - 1)
    return [[0] * i + list(g) + [0] * (k - 1 - i) for i in range(k)]


def _de_paridade(q: int, cols: list[list[int]]) -> list[list[int]]:
    """G = [I_k | P] a partir das colunas de H = [A | I_r] (as k primeiras colunas são A)."""
    r = len(cols[0])
    k = len(cols) - r
    for i in range(r):
        if cols[k + i] != [1 if t == i else 0 for t in range(r)]:
            raise ValueError("H não termina em I_r")
    # H·c = 0 com c = (u, v): A·u + v = 0, então v = -A·u.
    return [[1 if t == j else 0 for t in range(k)] + [(-cols[j][i]) % q for i in range(r)] for j in range(k)]


def _hamming(q: int, r: int) -> list[list[int]]:
    """Hamming sobre Z_q (q primo): um representante de cada ponto projetivo, unitários no fim."""
    pts = []
    for v in itertools.product(range(q), repeat=r):
        lider = next((x for x in v if x), 0)
        if lider == 1 and sum(1 for x in v if x) > 1:
            pts.append(list(v))
    unit = [[1 if t == i else 0 for t in range(r)] for i in range(r)]
    return _de_paridade(q, pts + unit)


def construcoes() -> list[dict]:
    """As construções versionadas. As colunas de paridade dos códigos `[n, k]_q` com raio
    r - 1 (chave p do Kéri) e o [19,6]_2 de raio 5 (K2(19,5) ≤ 64, Graham–Sloane na tabela do
    Kéri) saíram de busca local; o juiz é o verificador, não a busca."""
    golay2 = _sistematico(2, _ciclico(2, 23, [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1]))
    golay3 = _sistematico(3, _ciclico(3, 11, [2, 0, 1, 2, 1, 1]))
    cs = [
        (2, 15, 1, _hamming(2, 4), "código de Hamming binário [15,11]", "h"),
        (2, 23, 3, golay2, "código de Golay binário [23,12] (cíclico, g = 1+x²+x⁴+x⁵+x⁶+x¹⁰+x¹¹)", "h"),
        (3, 11, 2, golay3, "código de Golay ternário [11,6] (cíclico, g = 2+x²+2x³+x⁴+x⁵)", "h"),
        (5, 6, 1, _hamming(5, 2), "código de Hamming [6,4]_5", "h"),
        (7, 8, 1, _hamming(7, 2), "código de Hamming [8,6]_7", "h"),
    ]
    paridade = {
        (7, 6, 2): [[2, 1, 6], [4, 6, 4], [6, 5, 3]],
        (7, 7, 4): [[3, 3, 4, 6, 6], [0, 5, 3, 2, 5]],
        (11, 7, 2): [[7, 7, 3], [5, 10, 4], [4, 9, 5], [9, 2, 8]],
        (13, 8, 2): [[3, 4, 5], [3, 11, 6], [2, 4, 7], [5, 9, 1], [10, 4, 6]],
        (13, 8, 3): [[4, 11, 9, 9], [7, 11, 8, 10], [1, 8, 10, 2], [2, 9, 1, 3]],
        (2, 19, 5): [[1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1],
                     [1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0], [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                     [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1]],
    }
    for (q, n, R), A in paridade.items():
        r = len(A[0])
        unit = [[1 if t == i else 0 for t in range(r)] for i in range(r)]
        chave = "y" if (q, n, R) == (2, 19, 5) else "p"  # a chave é a da tabela do Kéri daquela célula
        cs.append((q, n, R, _de_paridade(q, A + unit), f"código linear [{n},{n - r}]_{q} de raio {R}", chave))
    return [{"q": q, "n": n, "R": R, "gerador": G, "construcao": c, "chave_keri": ch}
            for q, n, R, G, c, ch in cs]


def gravar() -> list[Path]:
    LIN.mkdir(parents=True, exist_ok=True)
    feitos = []
    for d in construcoes():
        q, n, R, G = d["q"], d["n"], d["R"], d["gerador"]
        if not cobre_por_sindromes(q, n, R, G):
            raise SystemExit(f"K{q}({n},{R}): construção não cobre")
        p = LIN / f"K{q}_{n}_{R}_M{q ** len(G)}.json"
        linhas = ["{", f' "q": {q}, "n": {n}, "R": {R},',
                  f' "construcao": {json.dumps(d["construcao"], ensure_ascii=False)},',
                  f' "chave_keri": "{d["chave_keri"]}",', ' "gerador": [']
        linhas += [f"  {json.dumps(g)}" + ("," if i < len(G) - 1 else "") for i, g in enumerate(G)]
        linhas += [" ]", "}"]
        p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        feitos.append(p)
    return feitos


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gravar", action="store_true", help="(re)grava os JSON das construções")
    a = ap.parse_args(argv)
    if a.gravar:
        for p in gravar():
            print(p.relative_to(RAIZ))
    for (q, n, R), (M, p, _G, c) in sorted(ler_lineares().items()):
        print(f"K{q}({n},{R}) ≤ {M}: {c} [{p.name}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
