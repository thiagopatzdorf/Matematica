"""Red team de K_7(5,3) = 17, ataque 2: os cubos de um perfil cobrem todo o espaço?

Um perfil fechado por cubos (rodar.py --cubos L, aqui L = M) é UNSAT se, e só se, (i) todo modelo
da CNF do perfil tem a coordenada 1 igual a algum cubo e (ii) cada cubo (CNF + unitárias) é UNSAT.
Este script ataca (i) por dois caminhos independentes do `fib_cubos.py` e confere os registros:

  enumerar   lista, por um algoritmo escrito aqui, todas as atribuições da coordenada 1 (as M
             palavras) que satisfazem o ENUNCIADO das restrições que só falam dela: fibra exata
             t1, (d) não decrescente no bloco, (e) primeiro bloco de a + 1 não antes do de a
             (mesma classe), (h) blocos consecutivos de mesmo tamanho em ordem lexicográfica.
  conferir   (com registros) cada índice 0..N-1 tem UNSAT + lrat_check VERIFIED, o cubo gravado é
             o da posição na lista ordenada, e o sha256 da CNF de cada cubo, regenerada com o
             codificador auditado (mesmo rótulo do rodar.py), é igual ao registrado.
  cobertura  prova por SAT, sem confiar em enumerador nenhum: toma as cláusulas da CNF auditada
             do perfil que não tocam variáveis das coordenadas >= 2 (nem as vizinhas delas:
             subconjunto de cláusulas = relaxação), soma uma cláusula de bloqueio por cubo e
             pede UNSAT ao CaDiCaL com prova LRAT conferida por lrat-check (e cake_lpr se
             CAKE_LPR existir). UNSAT => todo modelo da CNF inteira cai em algum cubo.

Uso:
  k753_cubos.py DIR_FIBRAS enumerar  q n M smin t0 t1 t2 t3 t4
  k753_cubos.py DIR_FIBRAS conferir  q n M smin ordem inst ARQ.jsonl [ARQ.jsonl ...]
  k753_cubos.py DIR_FIBRAS cobertura q n M smin ordem inst DIR_TMP"""
import hashlib
import json
import os
import subprocess
import sys
import time


def enumerar(q, M, t0, t1):
    """Atribuições da coordenada 1, por blocos: cada bloco recebe um multiconjunto (sequência
    não decrescente) dos símbolos restantes; (e) e (h) checados no fim e podados no caminho."""
    tam = list(t0)
    resto = list(t1)
    out = []
    seq = []  # sequências dos blocos

    def ok_e():
        primeiro = {}
        for b, s in enumerate(seq):
            for a in s:
                primeiro.setdefault(a, b)
        for a in range(q - 1):
            if t1[a] != t1[a + 1]:
                continue
            if (a + 1) in primeiro and (a not in primeiro or primeiro[a] > primeiro[a + 1]):
                return False
        return True

    def multis(k, mini, cur):
        if k == 0:
            yield tuple(cur)
            return
        for a in range(mini, q):
            if resto[a] == 0:
                continue
            resto[a] -= 1
            cur.append(a)
            yield from multis(k - 1, a, cur)
            cur.pop()
            resto[a] += 1

    def rec(b):
        if b == len(tam):
            if all(r == 0 for r in resto) and ok_e():
                out.append(tuple(a for s in seq for a in s))
            return
        for s in list(multis(tam[b], 0, [])):
            if b > 0 and tam[b] == tam[b - 1] and tam[b] > 0 and seq[-1] > s:
                continue
            for a in s:
                resto[a] -= 1
            seq.append(s)
            if ok_e():
                rec(b + 1)
            seq.pop()
            for a in s:
                resto[a] += 1

    rec(0)
    return sorted(set(out))


def ler(s):
    return tuple(int(c) for c in s)  # tipos de M = 16 com q = 7 e s_min = 1 só têm partes <= 9 aqui


def carregar_enc(d):
    sys.path.insert(0, d)
    import fib_encode as enc
    return enc


def perfil(enc, q, n, M, smin, ordem, inst):
    _, ins = enc.instancias(q, n, M, n, smin, ordem=ordem)
    return ins[inst]


def main():
    d, modo = sys.argv[1], sys.argv[2]
    q, n, M, smin = map(int, sys.argv[3:7])
    if modo == "enumerar":
        ts = [ler(s) for s in sys.argv[7:7 + n]]
        t0 = time.time()
        cubos = enumerar(q, M, ts[0], ts[1])
        print(json.dumps({"tipos": sys.argv[7:7 + n], "cubos": len(cubos), "s": round(time.time() - t0, 1)}))
        return
    ordem, inst = sys.argv[7], int(sys.argv[8])
    enc = carregar_enc(d)
    pref = perfil(enc, q, n, M, smin, ordem, inst)
    tipos = ["".join(map(str, t)) for t in pref]
    meus = enumerar(q, M, pref[0], pref[1])
    if modo == "conferir":
        import fib_cubos
        # o enumerador do repo é lento (enumera sem (h) e filtra); SEM_REPO=1 pula a comparação
        repo = None if os.environ.get("SEM_REPO") else fib_cubos.atribuicoes_coord1(q, M, pref[0], pref[1], smin, M)
        regs = {}
        ruins = 0
        for arq in sys.argv[9:]:
            for ln in open(arq, errors="replace"):
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if r.get("L") != M or r["inst"] != inst or r.get("ordem", "min") != ordem or r.get("sem"):
                    continue
                if r["tipos"] != tipos:
                    ruins += 1
                    continue
                if r["resultado"] == "UNSAT" and r.get("lrat_check") == "VERIFIED":
                    regs.setdefault(r["cubo_idx"], r)
        cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin)
        rot = f"K_{q}({n},{n-2}) M={M} k={n} s_min={smin} inst {inst}: {pref}"
        corpo = "".join(" ".join(map(str, c)) + " 0\n" for c in cnf.cl)
        sha_ok = sha_ruim = cubo_ruim = 0
        exemplos = []
        for ci, r in sorted(regs.items()):
            cubo = meus[ci] if ci < len(meus) else None
            if cubo is None or r["cubo"] != "".join(map(str, cubo)):
                cubo_ruim += 1
                exemplos.append(("cubo", ci))
                continue
            unit = "".join(f"{x[w][1][a]} 0\n" for w, a in enumerate(cubo))
            txt = (f"c {rot} cubo L={M} #{ci}: {list(cubo)}\np cnf {cnf.nv} {len(cnf.cl) + M}\n" + corpo + unit)
            if hashlib.sha256(txt.encode()).hexdigest() == r["sha256.cnf"]:
                sha_ok += 1
            else:
                sha_ruim += 1
                exemplos.append(("sha", ci))
        faltam = [i for i in range(len(meus)) if i not in regs]
        print(json.dumps({"inst": inst, "ordem": ordem, "tipos": tipos, "cubos_meus": len(meus),
                          "cubos_repo": None if repo is None else len(repo), "listas_iguais": None if repo is None else meus == repo,
                          "indices_fechados": len(regs), "faltam": len(faltam), "faltam_ex": faltam[:20],
                          "fora_do_intervalo": sum(1 for i in regs if i >= len(meus)),
                          "cubo_gravado_diverge": cubo_ruim, "sha_cnf_igual": sha_ok, "sha_cnf_diverge": sha_ruim,
                          "registros_com_tipos_errados": ruins, "exemplos": exemplos[:10]}, ensure_ascii=False))
        return
    if modo == "cobertura":
        tmp = sys.argv[9]
        cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin)
        # fecho transitivo a partir das variáveis das coordenadas >= 2 pela co-ocorrência em
        # cláusulas, sem nunca entrar nas da coordenada 1: pega P, y, contadores e (g) delas.
        # Qualquer subconjunto de cláusulas é relaxação; este guarda one-hot, fibra, (d), (e), (h).
        x1 = {v for w in range(M) for v in x[w][1]}
        viz = {v for w in range(M) for i in range(2, n) for v in x[w][i]}
        por_var = {}
        for ci, c in enumerate(cnf.cl):
            for l in c:
                por_var.setdefault(abs(l), []).append(ci)
        pilha = list(viz)
        while pilha:
            v = pilha.pop()
            for ci in por_var.get(v, ()):
                for l in cnf.cl[ci]:
                    u = abs(l)
                    if u not in viz and u not in x1:
                        viz.add(u)
                        pilha.append(u)
        rel = [c for c in cnf.cl if not any(abs(l) in viz for l in c)]
        bloq = [[-x[w][1][a] for w, a in enumerate(cubo)] for cubo in meus]
        base = os.path.join(tmp, f"cob_{q}{n}{M}_{ordem}_{inst}")
        with open(base + ".cnf", "w") as f:
            f.write(f"c relaxacao do perfil {inst} ({ordem}) {tipos} + {len(bloq)} bloqueios\n")
            f.write(f"p cnf {cnf.nv} {len(rel) + len(bloq)}\n")
            for c in rel + bloq:
                f.write(" ".join(map(str, c)) + " 0\n")
        out = {"inst": inst, "ordem": ordem, "tipos": tipos, "cubos": len(meus), "clausulas_cnf": len(cnf.cl),
               "clausulas_relaxadas": len(rel), "vars_excluidas": len(viz)}
        t = time.time()
        c = subprocess.run([os.environ["CADICAL"], base + ".cnf", "--lrat", "--binary=false", base + ".lrat"],
                           capture_output=True, text=True)
        out["cadical_rc"] = c.returncode
        out["cadical_s"] = round(time.time() - t, 1)
        if c.returncode == 20:
            c = subprocess.run([os.environ["LRAT_CHECK"], base + ".cnf", base + ".lrat"], capture_output=True, text=True)
            out["lrat_check"] = "VERIFIED" if "VERIFIED" in c.stdout and "NOT VERIFIED" not in c.stdout else c.stdout[-200:]
            if os.environ.get("CAKE_LPR"):
                c = subprocess.run([os.environ["CAKE_LPR"], base + ".cnf", base + ".lrat"], capture_output=True, text=True)
                out["cake_lpr"] = c.stdout.strip().splitlines()[-1] if c.stdout.strip() else c.stderr[-200:]
            h = hashlib.sha256(open(base + ".cnf", "rb").read()).hexdigest()
            out["sha256.cnf"] = h
        elif c.returncode == 10:
            # um modelo da relaxação fora de todos os cubos: mostra a coordenada 1
            v = {int(t) for ln in c.stdout.splitlines() if ln.startswith("v ") for t in ln[2:].split()}
            out["fora_dos_cubos"] = "".join(str(next((a for a in range(q) if x[w][1][a] in v), "?")) for w in range(M))
        for ext in (".cnf", ".lrat"):
            if os.path.exists(base + ext):
                os.remove(base + ext)
        # controle de poder: sem o bloqueio de um cubo sorteado, a relaxação tem de ser SAT e o
        # modelo tem de cair exatamente nesse cubo (os bloqueios não são vazios por engano)
        import random
        k = random.Random(inst).randrange(len(meus))
        with open(base + "_ctl.cnf", "w") as f:
            f.write(f"p cnf {cnf.nv} {len(rel) + len(bloq) - 1}\n")
            for c in rel + bloq[:k] + bloq[k + 1:]:
                f.write(" ".join(map(str, c)) + " 0\n")
        c = subprocess.run([os.environ["CADICAL"], base + "_ctl.cnf"], capture_output=True, text=True)
        os.remove(base + "_ctl.cnf")
        v = {int(t) for ln in c.stdout.splitlines() if ln.startswith("v ") for t in ln[2:].split()}
        achado = "".join(str(next((a for a in range(q) if x[w][1][a] in v), "?")) for w in range(M))
        out["controle"] = {"cubo_liberado": k, "rc": c.returncode, "modelo_no_cubo": achado == "".join(map(str, meus[k]))}
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
