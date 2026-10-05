#!/usr/bin/env python3
"""Baseline congelado: o polinômio do recorde RSA-896 (Weis, 2026-09-19), conferido por aritmética exata.

    python3 tools/fatoracao/baseline_rsa896.py verificar tools/fatoracao/baseline/rsa896.json
    python3 tools/fatoracao/baseline_rsa896.py verificar rsa896.json --cado <pasta do cado-nfs>   # recalcula alpha e Murphy-E
    python3 tools/fatoracao/baseline_rsa896.py congelar post.html lista.txt --cado <pasta> --saida rsa896.json

Por que existe: número copiado por resumidor automático troca dígito (aconteceu com um fator de 135 dígitos deste mesmo
post). Aqui nada é digitado: `congelar` extrai do texto cru e só grava se as conferências fecharem; `verificar` refaz
as conferências que não dependem de ninguém:

* `p` e `q` são primos e `p*q == N`, e `N` é o do RSA-896 da lista do desafio (segunda fonte);
* o resultante `Res(f,g)` é exatamente o valor que o post declara (`-8N`): o polinômio serve para este `N`;
* com `--cado`: `alpha` e o Murphy-E recalculados batem com os do post, com os limites que o CADO deriva dos
  parâmetros de crivo (`area = 2^A * qmin`, `Bf = 2^lpb1`, `Bg = 2^lpb0`, em cadotask.py).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from medir_cado import eh_primo  # noqa: E402

GRAU = 6


def so_digitos(texto):
    return int(re.sub(r"[^\d]", "", texto))


def blocos_pre(html):
    return re.findall(r"<pre>(.*?)</pre>", html, flags=re.S)


def extrair_post(html):
    """Do texto cru do post: N, p, q, o polinômio, o skew e os parâmetros de crivo. Nada é digitado à mão."""
    pre = blocos_pre(html)
    n = so_digitos(next(b for b in pre if b.lstrip().startswith("RSA-") and "=" in b).split("=", 1)[1])
    pq = next(b for b in pre if b.lstrip().startswith("p ="))
    p = so_digitos(re.search(r"p =(.*?)q =", pq, flags=re.S).group(1))
    q = so_digitos(pq.split("q =", 1)[1])
    poly = next(b for b in pre if "Y0:" in b)
    campo = {k: re.sub(r"\s+", "", v) for k, v in re.findall(
        r"(Y0|Y1|c\d|skew):\s*(-?[\d.\s]+?)(?=\n[A-Za-z]|\Z)", poly.strip() + "\n", flags=re.S)}
    crivo = next(b for b in pre if "lpb" in b)
    lpb = [int(x) for x in re.search(r"lpb\s+(\d+)\s+(\d+)", crivo).groups()]
    return {"n": n, "p": p, "q": q,
            "poly": {"c": [int(campo[f"c{i}"]) for i in range(GRAU + 1)], "Y0": int(campo["Y0"]), "Y1": int(campo["Y1"]),
                     "skew": float(campo["skew"])},
            "crivo": {"A": int(re.search(r"A = (\d+)", html).group(1)), "qmin": float(re.search(r"qmin:\s*([\d.e+]+)", crivo).group(1)),
                      "lpb0": lpb[0], "lpb1": lpb[1]},
            "declarado": {"alpha": float(re.search(r"alpha (-?[\d.]+)", html).group(1)),
                          "murphy_e": float(re.search(r"Murphy E ([\d.e+-]+)", html).group(1)),
                          "resultante_sobre_n": int(re.search(r"Res\(f,g\) = (-?\d+)N", html).group(1))}}


def valor_da_lista(wikitext, nome):
    """O N de `nome` na lista do desafio (texto cru da Wikipedia): a segunda fonte independente."""
    i = wikitext.index(f"=== {nome}")
    return so_digitos(re.search(rf"{nome} = (\d[\d\s]*)", wikitext[i:i + 3000]).group(1))


def resultante(poly):
    """Res(f, g) com g = Y1*x + Y0 e f de grau 6: soma de c_i * (-Y0)^i * Y1^(6-i). Inteiro exato."""
    c, y0, y1 = poly["c"], poly["Y0"], poly["Y1"]
    return sum(c[i] * (-y0) ** i * y1 ** (GRAU - i) for i in range(GRAU + 1))


def conferencias(d):
    """Cada conferência é um booleano; o baseline só vale se todas forem verdadeiras."""
    n, p, q = int(d["n"]), int(d["p"]), int(d["q"])
    res = resultante(d["poly"])
    return {"p_primo": eh_primo(p), "q_primo": eh_primo(q), "p_vezes_q_igual_n": p * q == n,
            "n_igual_ao_da_lista": n == int(d["n_lista"]),
            "resultante_multiplo_de_n": res % n == 0,
            "resultante_igual_ao_declarado": res == d["declarado"]["resultante_sobre_n"] * n}


def parametros_murphy(crivo):
    """Os limites que o CADO usa para o Murphy-E da seleção (cadotask.py): area = 2^A*qmin, Bf = 2^lpb1, Bg = 2^lpb0."""
    return {"area": 2.0 ** crivo["A"] * crivo["qmin"], "Bf": float(2 ** crivo["lpb1"]), "Bg": float(2 ** crivo["lpb0"])}


def arquivo_poly(d):
    p = d["poly"]
    return (f"n: {d['n']}\nskew: {p['skew']}\n" + "".join(f"c{i}: {v}\n" for i, v in enumerate(p["c"]))
            + f"Y0: {p['Y0']}\nY1: {p['Y1']}\n")


def medir_com_cado(d, cado, tmp):
    """alpha e Murphy-E recalculados pelas ferramentas compiladas do CADO."""
    ferr = Path(cado) / "build" / "vm" / "polyselect"
    arq = Path(tmp) / "rsa896.poly"
    arq.write_text(arquivo_poly(d), encoding="utf-8")
    saida_alpha = subprocess.run([str(ferr / "alpha"), "-poly", str(arq), "-B", "2000"], capture_output=True, text=True).stdout
    alpha = float(re.search(r"alpha\(poly1\) = (-?[\d.]+)", saida_alpha).group(1))
    m = parametros_murphy(d["crivo"])
    saida = subprocess.run([str(ferr / "score"), str(arq), "-Bf", f"{m['Bf']:.10e}", "-Bg", f"{m['Bg']:.10e}",
                            "-area", f"{m['area']:.10e}"], capture_output=True, text=True).stdout
    return {"alpha": alpha, "murphy_e": float(saida.strip().splitlines()[-1])}


def bate(medido, declarado, rel=1e-3):
    return abs(medido - declarado) <= rel * abs(declarado)


def congelar(html, wikitext, cado, tmp):
    d = extrair_post(html)
    d["n_lista"] = valor_da_lista(wikitext, "RSA-896")
    medidas = medir_com_cado(d, cado, tmp)
    ok = all(conferencias({**d, "n": d["n"], "p": d["p"], "q": d["q"]}).values())
    if not ok or not bate(medidas["alpha"], d["declarado"]["alpha"], 5e-3) or not bate(medidas["murphy_e"], d["declarado"]["murphy_e"]):
        raise ValueError(f"o baseline não fecha: {conferencias(d)} {medidas} {d['declarado']}")
    return {"formato": "baseline-polinomio/v1", "numero": "RSA-896", "fonte": "https://saweis.net/posts/rsa-896.html",
            "coletado_em": "2026-10-04", "sha256_post": hashlib.sha256(html.encode("utf-8")).hexdigest(),
            "n": str(d["n"]), "n_lista": str(d["n_lista"]), "p": str(d["p"]), "q": str(d["q"]),
            "poly": d["poly"], "crivo": d["crivo"], "declarado": d["declarado"],
            "murphy_parametros": parametros_murphy(d["crivo"]),
            "reproduzido_com_cado": {**medidas, "cado_commit": subprocess.run(
                ["git", "-C", str(cado), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verificar")
    v.add_argument("arquivo")
    v.add_argument("--cado")
    c = sub.add_parser("congelar")
    c.add_argument("post")
    c.add_argument("lista")
    c.add_argument("--cado", required=True)
    c.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "congelar":
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            dados = congelar(Path(a.post).read_text(encoding="utf-8"), Path(a.lista).read_text(encoding="utf-8"), a.cado, tmp)
        Path(a.saida).write_text(json.dumps(dados, indent=1) + "\n", encoding="utf-8")
        print("congelado em", a.saida, dados["reproduzido_com_cado"])
        return 0
    d = json.loads(Path(a.arquivo).read_text(encoding="utf-8"))
    r = conferencias(d)
    if a.cado:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            m = medir_com_cado(d, a.cado, tmp)
        r["alpha_bate_com_o_post"] = bate(m["alpha"], d["declarado"]["alpha"], 5e-3)
        r["murphy_e_bate_com_o_post"] = bate(m["murphy_e"], d["declarado"]["murphy_e"])
    print(json.dumps(r, indent=1))
    return 0 if all(r.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
