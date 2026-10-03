#!/usr/bin/env python3
"""Esqueleto do loop de recordes: gerar -> verificar -> registrar -> certificar.

Para UMA célula K_q(n,R):

1. roda o GERADOR (comando configurável) que escreve um código num arquivo;
2. roda o VERIFICADOR (comando configurável; padrão: verify_cover.py; o
   tools/verify do agente B entra aqui quando existir);
3. registra a tentativa em ledger/runs.jsonl com os seis campos de
   proveniência {gerador, commit, seed, comando, data, agente}; se o código
   verificado melhora o nosso estado, atualiza ledger/ours.json e a célula em
   ledger/cells.json, copia o código para data/codes/ e grava o registro em
   ledger/provenance.json;
4. prepara a pasta do certificado Lean (certs/K<q>_<n>_<R>_M<M>/) para o
   agente A: o código, um CERT.json e um README com o que falta.

Modo seco é o PADRÃO: mostra o plano e não roda nada nem escreve nada.
`--executar` faz de verdade. Nada de busca pesada aqui: o gerador padrão
(gen_greedy.py) só aceita q^n pequeno.

Placeholders nos comandos: {q} {n} {R} {saida} {arquivo} {seed}.

Exemplos:
    python3 scripts/loop/record_loop.py --celula "K2(4,1)"            # seco
    python3 scripts/loop/record_loop.py --celula "K2(4,1)" --executar
    python3 scripts/loop/record_loop.py --celula "K7(9,4)" \\
        --gerador "./meu_gerador {q} {n} {R} {saida}" \\
        --verificador "tools/verify {arquivo} {q} {n} {R}" --executar
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ledger"))
import build as ledger_build  # noqa: E402

GERADOR_PADRAO = "{py} scripts/loop/gen_greedy.py {q} {n} {R} {saida} --seed {seed}"
VERIFICADOR_PADRAO = "{py} scripts/loop/verify_cover.py {arquivo} {q} {n} {R}"


def parse_celula(s: str) -> tuple[int, int, int]:
    m = re.fullmatch(r"\s*K_?\{?(\d+)\}?\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*", s)
    if not m:
        m = re.fullmatch(r"\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*", s)
    if not m:
        raise SystemExit(f"célula inválida: {s!r} (use K2(4,1) ou 2,4,1)")
    return tuple(int(x) for x in m.groups())  # type: ignore[return-value]


def sha256_arquivo(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def contar_palavras(p: Path) -> int:
    return sum(1 for linha in p.read_text().splitlines() if linha.split("#", 1)[0].strip())


def commit_atual(raiz: Path) -> str | None:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz, capture_output=True,
                             text=True, check=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain"], cwd=raiz, capture_output=True,
                              text=True, check=True).stdout.strip()
        return sha + ("+sujo" if sujo else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def formatar(cmd: str, **kw) -> list[str]:
    kw = {k: str(v) for k, v in kw.items()}
    return [parte.format(**kw) for parte in shlex.split(cmd)]


def rodar(argv: list[str], cwd: Path, tempo: int) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=tempo)


def ultima_linha_json(texto: str) -> dict | None:
    for linha in reversed(texto.strip().splitlines()):
        try:
            v = json.loads(linha)
            if isinstance(v, dict):
                return v
        except json.JSONDecodeError:
            continue
    return None


def ler_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def gravar_json(p: Path, dados: dict) -> None:
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preparar_certificado(certs: Path, q: int, n: int, R: int, M: int, codigo: Path,
                         sha: str, prov_id: str, verif: dict | None) -> Path:
    pasta = certs / f"K{q}_{n}_{R}_M{M}"
    pasta.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(codigo, pasta / "code.txt")
    declaracao = f"CoveringKernel.K{q}_{n}_{R}_le_{M}_kernel"
    gravar_json(pasta / "CERT.json", {
        "cell": f"K{q}({n},{R})", "q": q, "n": n, "R": R, "M": M,
        "code": "code.txt", "sha256": sha,
        "declaracao_prevista": declaracao,
        "enunciado": f"∃ C : Finset (Fin {n} → ZMod {q}), C.card = {M} ∧ CoveringA2.Covers {R} C",
        "estado": "aguardando_lean",
        "verificacao_computacional": verif,
        "provenance": prov_id,
    })
    (pasta / "README.md").write_text(
        f"# Certificado pendente: K{q}({n},{R}) ≤ {M}\n\n"
        f"Preparado pelo `scripts/loop/record_loop.py`. O código (`code.txt`, sha256 `{sha}`)\n"
        f"passou no verificador computacional; falta o teorema Lean (agente A):\n\n"
        f"    theorem {declaracao} :\n"
        f"        ∃ C : Finset (Fin {n} → ZMod {q}), C.card = {M} ∧ CoveringA2.Covers {R} C\n\n"
        f"Quando o teorema compilar: preencher `ours_lean` em `ledger/ours.json`\n"
        f"(M, declaration, tag), rodar `python3 ledger/build.py` e trocar `estado` em\n"
        f"`CERT.json` para `provado`.\n", encoding="utf-8")
    return pasta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--celula", required=True, help='ex.: "K2(4,1)" ou 2,4,1')
    ap.add_argument("--executar", action="store_true", help="faz de verdade (padrão: seco)")
    ap.add_argument("--seco", action="store_true", help="só mostra o plano (é o padrão)")
    ap.add_argument("--gerador", default=GERADOR_PADRAO)
    ap.add_argument("--verificador", default=VERIFICADOR_PADRAO)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--agente", default=os.environ.get("JAMES_AGENTE", "desconhecido"))
    ap.add_argument("--tempo-limite", type=int, default=600)
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="raiz do repositório (cwd dos comandos)")
    ap.add_argument("--ledger-dir", type=Path, help="padrão: <raiz>/ledger")
    ap.add_argument("--codes-dir", type=Path, help="padrão: <raiz>/data/codes")
    ap.add_argument("--certs-dir", type=Path, help="padrão: <raiz>/certs")
    ap.add_argument("--runs-dir", type=Path, help="padrão: <raiz>/runs (fora do git)")
    a = ap.parse_args(argv)

    raiz = a.raiz.resolve()
    ldir = (a.ledger_dir or raiz / "ledger").resolve()
    codes = (a.codes_dir or raiz / "data" / "codes").resolve()
    certs = (a.certs_dir or raiz / "certs").resolve()
    runs = (a.runs_dir or raiz / "runs").resolve()
    q, n, R = parse_celula(a.celula)
    k = ledger_build.chave(q, n, R)

    ledger = ledger_build.carregar(ldir / "cells.json")
    cel = next((c for c in ledger["cells"] if (c["q"], c["n"], c["R"]) == (q, n, R)), None)
    if cel is None:
        raise SystemExit(f"{ledger_build.nome(q, n, R)} não está no ledger")
    pub_ub = cel["published"]["ub"]["value"] if cel["published"]["ub"] else None
    pub_lb = cel["published"]["lb"]["value"] if cel["published"]["lb"] else None

    agora = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    carimbo = agora.strftime("%Y%m%dT%H%M%SZ")
    pasta_run = runs / f"K{q}_{n}_{R}" / carimbo
    saida = pasta_run / "code.txt"
    # Caminho relativo à raiz (cwd dos comandos) deixa o comando registrado
    # reprodutível em outra máquina; idem "python3" em vez do executável absoluto.
    saida_cmd = Path(_rel(saida, raiz))
    py = "python3" if shutil.which("python3") else shlex.quote(sys.executable)
    cmd_ger = formatar(a.gerador.replace("{py}", py), q=q, n=n, R=R, saida=saida_cmd, seed=a.seed,
                       arquivo=saida_cmd)
    cmd_ver = formatar(a.verificador.replace("{py}", py), q=q, n=n, R=R, saida=saida_cmd, seed=a.seed,
                       arquivo=saida_cmd)

    print(f"célula {cel['id']}: publicado lb={pub_lb} ub={pub_ub}; "
          f"nosso comp={cel.get('ours_computational') and cel['ours_computational']['M']} "
          f"lean={cel.get('ours_lean') and cel['ours_lean']['M']}; q^n={cel['space']:.3g}")
    print("gerador:     " + shlex.join(cmd_ger))
    print("verificador: " + shlex.join(cmd_ver))
    if not a.executar:
        print(f"SECO: rodaria em {pasta_run}, registraria em {ldir / 'runs.jsonl'}, "
              f"e se melhorar o nosso estado: {ldir / 'ours.json'}, {codes}/, {certs}/. Use --executar.")
        return 0

    pasta_run.mkdir(parents=True, exist_ok=True)
    g = rodar(cmd_ger, raiz, a.tempo_limite)
    (pasta_run / "gerador.log").write_text(g.stdout + g.stderr)
    registro = {
        "cell": cel["id"], "q": q, "n": n, "R": R,
        "provenance": {"gerador": a.gerador, "commit": commit_atual(raiz), "seed": a.seed,
                       "comando": shlex.join(cmd_ger), "data": agora.isoformat(), "agente": a.agente},
        "verificador": shlex.join(cmd_ver), "run_dir": _rel(pasta_run, raiz),
    }
    if g.returncode != 0 or not saida.exists():
        registro.update(ok=False, etapa="gerador", codigo_saida=g.returncode)
        return _fechar(ldir, registro, 3, "gerador falhou (ver gerador.log)")

    v = rodar(cmd_ver, raiz, a.tempo_limite)
    (pasta_run / "verificador.log").write_text(v.stdout + v.stderr)
    verif = ultima_linha_json(v.stdout)
    M = contar_palavras(saida)
    sha = sha256_arquivo(saida)
    registro.update(M=M, sha256=sha, verificacao=verif)
    if v.returncode != 0:
        registro.update(ok=False, etapa="verificador", codigo_saida=v.returncode)
        return _fechar(ldir, registro, 4, f"verificador reprovou M={M}")
    if verif and "M" in verif and verif["M"] != M:
        registro.update(ok=False, etapa="verificador", erro="M do verificador != linhas do arquivo")
        return _fechar(ldir, registro, 4, "contagem divergente")

    ours = ler_json(ldir / "ours.json")
    atual = ours.setdefault("cells", {}).get(k, {})
    melhores = [x["M"] for x in (atual.get("ours_computational"), atual.get("ours_lean")) if x]
    melhora = not melhores or M < min(melhores)
    registro.update(ok=True, melhora_nosso=melhora, bate_publicado=pub_ub is not None and M < pub_ub)
    if not melhora:
        return _fechar(ldir, registro, 0, f"verificado M={M}, não melhora o nosso ({min(melhores)})")

    destino = codes / f"q{q}_n{n}_R{R}_M{M}.txt"
    codes.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(saida, destino)
    prov_id = f"P-K{q}_{n}_{R}-M{M}-{carimbo}"
    prov = ler_json(ldir / "provenance.json")
    prov.setdefault("registros", {})[prov_id] = {"codigo": _rel(destino, raiz), **registro["provenance"]}
    gravar_json(ldir / "provenance.json", prov)

    atual["ours_computational"] = {"M": M, "file": _rel(destino, raiz), "sha256": sha, "provenance": prov_id}
    atual.setdefault("ours_lean", None)
    ours["cells"][k] = atual
    ours["atualizado"] = agora.date().isoformat()
    gravar_json(ldir / "ours.json", ours)
    ledger_build.aplicar_nosso(cel, atual)
    ledger["meta"]["ours_atualizado"] = ours["atualizado"]
    ledger_build.escrever(ledger, ldir / "cells.json")

    pasta_cert = preparar_certificado(certs, q, n, R, M, destino, sha, prov_id, verif)
    registro.update(code_file=_rel(destino, raiz), cert_dir=_rel(pasta_cert, raiz), provenance_id=prov_id)
    return _fechar(ldir, registro, 0, f"REGISTRADO {cel['id']} ≤ {M} "
                   f"({'bate' if registro['bate_publicado'] else 'não bate'} o publicado {pub_ub}); "
                   f"certificado em {pasta_cert}")


def _rel(p: Path, raiz: Path) -> str:
    try:
        return str(p.resolve().relative_to(raiz))
    except ValueError:
        return str(p)


def _fechar(ldir: Path, registro: dict, codigo: int, msg: str) -> int:
    with (ldir / "runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False, sort_keys=True) + "\n")
    print(msg)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
