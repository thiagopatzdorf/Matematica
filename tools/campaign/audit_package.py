#!/usr/bin/env python3
"""Pacote de auditoria de um witness: clona o repo limpo, compila os 4 verificadores,
roda cada um com parâmetros explícitos, testes negativos, e grava ambiente/tempo/memória.
Uso: audit_package.py q7_n9_R4_M1285 [--repo URL_OU_CAMINHO] [--ref REF]
Saída: campaigns/covering-codes/_auditoria/<nome>/{AUDITORIA.json,AUDITORIA.md,witness.txt}"""
import argparse, hashlib, json, os, platform, resource, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sh(cmd, cwd=None, env=None):
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out, time.time() - t0

def run(cmd, cwd=None):
    """exit, saída, relógio e pico de RSS do filho (ru_maxrss de RUSAGE_CHILDREN, delta por processo via wait4)."""
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout.read()
    _, status, ru = os.wait4(p.pid, 0)
    code = os.waitstatus_to_exitcode(status)
    return {"exit": code, "stdout": out.strip()[-400:], "wall_s": round(time.time() - t0, 3), "peak_rss_mb": round(ru.ru_maxrss / 1024, 1)}

def ver(cmd):
    return sh(cmd)[1].strip().splitlines()[0] if shutil.which(cmd[0]) else "indisponível"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("--repo", default=str(ROOT)); ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    b = a.name; q, n, R, M = (int(x[1:]) for x in b.split("_"))
    env = dict(os.environ); env["PATH"] = os.path.expanduser("~/.cargo/bin") + ":" + env["PATH"]
    tmp = Path(tempfile.mkdtemp(prefix="audit-"))
    try:
        c = tmp / "clone"
        rc, o, t_clone = sh(["git", "clone", "-q", a.repo, str(c)])
        assert rc == 0, o
        rc, o, _ = sh(["git", "checkout", "-q", a.ref], cwd=c); assert rc == 0, o
        commit = sh(["git", "rev-parse", "HEAD"], cwd=c)[1].strip()
        wit = c / "data/codes" / f"{b}.txt"
        sha = hashlib.sha256(wit.read_bytes()).hexdigest()
        build = {}
        rc, o, t = sh(["cc", "-O2", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", str(c / "verify-c"), str(c / "tools/verify/verify.c")]); build["c"] = {"exit": rc, "s": round(t, 1)}
        rc, o, t = sh(["cargo", "build", "--release", "--offline", "-q"], cwd=c / "tools/verify-rust", env=env); build["rust"] = {"exit": rc, "s": round(t, 1)}
        rc, o, t = sh(["go", "build", "-o", str(c / "verify-go"), "."], cwd=c / "tools/verify-cleanroom"); build["go"] = {"exit": rc, "s": round(t, 1)}
        def bins(Q, N, RR, MM):
            P = ["--q", str(Q), "--n", str(N), "--R", str(RR), "--M", str(MM)]
            return {
                "verify-c (C, bolas/bitset)": [str(c / "verify-c"), *P],
                "verify-rust (Rust, dilatação por camadas)": [str(c / "tools/verify-rust/target/release/verify-rust"), *P],
                "verify-py-dilation (Python/numpy)": [sys.executable, str(c / "tools/campaign/verify_cover_dilation.py"), "-q", str(Q), "-n", str(N), "-r", str(RR), "-m", str(MM)],
                "verify-cleanroom (Go, BFS multi-fonte)": [str(c / "verify-go"), *P],
            }
        def exits(path, Q=q, N=n, RR=R, MM=M):
            return {k: run(v + [str(path)])["exit"] for k, v in bins(Q, N, RR, MM).items()}
        res = {k: run(v + [str(wit)]) for k, v in bins(q, n, R, M).items()}
        neutro = tmp / "witness-neutro.txt"; shutil.copy(wit, neutro)
        lines = [l for l in wit.read_text().split("\n") if l]
        def variant(name, content, **kw):
            f = tmp / f"{name}.txt"; f.write_text("\n".join(content) + "\n")
            return exits(f, **kw)
        neg = {
            "uma_palavra_removida, M intacto (#distintas != M => exit 2)": variant("rm", lines[1:]),
            "duplicata (exit 2)": variant("dup", lines[:-1] + [lines[0]]),
            "simbolo_invalido (dígito >= q => exit 2)": variant("sym", [lines[0][:-1] + str(q)] + lines[1:]),
            "comprimento_errado (exit 2)": variant("len", [lines[0] + "0"] + lines[1:]),
            # nome neutro: o verify-c recusa (exit 2) parâmetros que contradizem o NOME do arquivo (guarda deliberada); aqui se testa a cobertura
            "R-1, arquivo com nome neutro (cobertura falha => exit 1)": exits(neutro, RR=R - 1),
            "R-1, arquivo com o nome original (verify-c: exit 2 por contradizer o nome; os outros: 1)": exits(wit, RR=R - 1),
            "M-1 declarado (exit 2)": exits(neutro, MM=M - 1),
        }
        # troca de uma palavra por outra qualquer fora do código muda a cobertura? Só registramos os exits.
        info = {
            "witness": b, "q": q, "n": n, "R": R, "M": M, "sha256_file": sha, "repo_commit": commit, "ref": a.ref,
            "linhas": len(lines), "distintas": len(set(lines)), "pontos_do_espaco": q ** n,
            "repro_cmd": f"git clone <repo> && git checkout {commit} && python3 tools/campaign/audit_package.py {b}",
            "ambiente": {"os": platform.platform(), "python": platform.python_version(), "numpy": ver([sys.executable, "-c", "import numpy;print(numpy.__version__)"]),
                         "gcc": ver(["cc", "--version"]), "rustc": ver(["rustc", "--version"]), "go": ver(["go", "version"]),
                         "cpu": next((l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "?"), "nproc": os.cpu_count()},
            "build": build, "verificadores": res, "negativos_exit_por_verificador": neg,
            "clone_s": round(t_clone, 1),
            "data_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        out = ROOT / "campaigns/covering-codes/_auditoria" / b; out.mkdir(parents=True, exist_ok=True)
        shutil.copy(wit, out / "witness.txt")
        (out / "AUDITORIA.json").write_text(json.dumps(info, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
        md = [f"# Pacote de auditoria: {b}", "", f"- SHA-256 do arquivo: `{sha}`", f"- commit auditado (clone limpo): `{commit}`", f"- {info['linhas']} linhas, {info['distintas']} distintas, {info['pontos_do_espaco']} pontos no espaço",
              f"- comando: `{info['repro_cmd']}`", f"- ambiente: {json.dumps(info['ambiente'], ensure_ascii=False)}", "", "| verificador | exit | tempo (s) | pico RSS (MB) | saída |", "|---|---|---|---|---|"]
        md += [f"| {k} | {v['exit']} | {v['wall_s']} | {v['peak_rss_mb']} | `{v['stdout'][:110]}` |" for k, v in res.items()]
        md += ["", "## Testes negativos (exit por verificador, na ordem acima)", ""] + [f"- {k}: {list(v.values())}" for k, v in neg.items()]
        (out / "AUDITORIA.md").write_text("\n".join(md) + "\n")
        print(json.dumps({k: v["exit"] for k, v in res.items()}), json.dumps(neg, ensure_ascii=False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
