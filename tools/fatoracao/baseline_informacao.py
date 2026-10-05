#!/usr/bin/env python3
"""Pipeline CONGELADO da linha de base de informação das relações (campanha de compressão, experimento central).

    python3 tools/fatoracao/baseline_informacao.py analisar saida.json --dev <captura>... --teste <captura>...
    python3 tools/fatoracao/baseline_informacao.py relatorio saida.json

Tudo o que o plano manda medir sai daqui, instância por instância e agregado por tamanho:
curva do núcleo, ponto de parada, novidade, destino das relações, previsibilidade com transferência entre tamanhos,
controles aleatórios, componentes do hipergrafo, compressibilidade e ajuste dos modelos de I(W).

Os parâmetros abaixo valem para qualquer conjunto; mudar um exige PR que diga o que mudou e por quê. O conjunto `dev` serve para
desenvolver; a evidência primária é a do conjunto `teste`, que só é coletado depois de este arquivo ser commitado.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import informacao_relacoes as inf  # noqa: E402
import relacoes as rel  # noqa: E402

PONTOS = 40            # prefixos de 5% a 100% das relações brutas
PONTOS_NULO = 20       # os controles usam menos pontos (custam o mesmo cada um)
SEMENTES_NULO = (0, 1)
MANTER = inf.MANTER    # 160, o excesso que o purge do CADO mantém
RIDGE = 1.0
RECALL_UTIL = 0.99
AMOSTRA_COMPRESSAO = 100000


def _primeiro(dados, predicado, curva_pontos):
    """Menor prefixo (em relações brutas) em que `predicado(estatísticas do núcleo)` passa, refinado por bisseção."""
    ant = 0
    for p in curva_pontos:
        if predicado({"linhas": p["linhas_nucleo"], "colunas": p["colunas_nucleo"], "excesso": p["excesso"]}):
            lo, hi = ant, p["t"]
            while hi - lo > max(1, dados.n_brutas // 2000):
                meio = (lo + hi) // 2
                st, _ = rel.nucleo(dados, meio)
                if predicado(st):
                    hi = meio
                else:
                    lo = meio
            return hi
        ant = p["t"]
    return None


def _parada(dados, c):
    t_fim = dados.n_brutas
    w_fim = inf.trabalho(dados, t_fim)[0]
    saida = {"t_final": t_fim, "w_sq_final": w_fim}
    for nome, pred in (("emergencia", lambda e: e["linhas"] > 0), ("excesso_zero", lambda e: e["linhas"] > 0 and e["excesso"] >= 0),
                       ("t_min", lambda e: e["excesso"] >= MANTER)):
        t = _primeiro(dados, pred, c)
        saida[nome] = None if t is None else {"t": t, "fracao_das_brutas": t / t_fim, "w_sq": inf.trabalho(dados, t)[0],
                                              "fracao_do_trabalho": inf.trabalho(dados, t)[0] / w_fim if w_fim else None}
    saida["margem_de_parada"] = None if saida["t_min"] is None else 1.0 - saida["t_min"]["fracao_das_brutas"]
    return saida


def _nulos(dados, c):
    saida = {}
    for modo in ("configuracao", "ordem"):
        rodadas = [inf.curva_nulo(dados, modo, semente=s, pontos=PONTOS_NULO) for s in SEMENTES_NULO]
        fim = [r[-1] for r in rodadas]
        k90 = int(np.argmin([abs(p["unicas"] - 0.9 * dados.n_unicas) for p in rodadas[0]]))
        emerg = []
        for r in rodadas:
            primeiro = next((p["unicas"] for p in r if p["linhas_nucleo"] > 0), None)
            emerg.append(None if primeiro is None else primeiro / dados.n_unicas)
        saida[modo] = {"linhas_nucleo_final": float(np.mean([f["linhas_nucleo"] for f in fim])),
                       "excesso_final": float(np.mean([f["excesso"] for f in fim])),
                       "excesso_em_90pct": float(np.mean([r[k90]["excesso"] for r in rodadas])),
                       "emergencia_fracao": None if None in emerg else float(np.mean(emerg))}
    real = c[-1]
    saida["real"] = {"linhas_nucleo_final": real["linhas_nucleo"], "excesso_final": real["excesso"]}
    return saida


def analisar_instancia(pasta, conjunto):
    """Todas as métricas de uma captura. Devolve `(resultado_json, material_para_transferencia)`."""
    dados = rel.carregar(pasta)
    man = dados.manifesto
    meta = man.get("meta", {})
    c = inf.curva(dados, PONTOS)
    validacao = rel.reproduz_purge_do_cado(dados)
    dest, _ = inf.destinos(dados, pasta)
    nu = dados.n_unicas
    fracoes = {inf.DESTINOS[k]: float((dest == k).mean()) for k in (1, 2, 3, 4)}
    w = [p["w_sq"] for p in c]
    modelos = {}
    for chave in ("excesso", "colunas_nucleo", "linhas_nucleo", "ideais_vistos"):
        r = inf.ajustar_modelos(w, [max(0, p[chave]) for p in c])
        modelos[chave] = {"vencedor": r["vencedor"], "bic": {k: v["bic"] for k, v in r["modelos"].items()},
                          "parametros": r["modelos"][r["vencedor"]]["params"]}
    nulos = _nulos(dados, c)
    caract, nomes = inf.caracteristicas_online(dados)
    par = man.get("parametros", {})
    comp = inf.compressibilidade(dados, max_rel=AMOSTRA_COMPRESSAO)
    cg = inf.componentes_grandes(dados, 10)
    resultado = {
        "id": Path(pasta).name, "conjunto": conjunto, "digitos": meta.get("digitos"), "commit_cado": man.get("commit_cado"),
        "commit_campanha": meta.get("commit_campanha"), "semente_bwc": meta.get("semente_bwc"),
        "sha256_manifesto": man.get("sha256"), "n_brutas": dados.n_brutas, "n_unicas": nu, "n_livres": dados.n_livres,
        "n_ideais": dados.n_ideais, "fracao_duplicatas": 1.0 - nu / dados.n_brutas, "livres_com_ideal_ruim": len(dados.livres_discrepantes),
        "lpb": [par.get("tasks.lpb0"), par.get("tasks.lpb1")], "valida_o_purge_do_cado": bool(validacao["inicio_bate"] and validacao["fim_bate"]),
        "purge_cado": man["purge"], "destinos_das_unicas": fracoes, "parada": _parada(dados, c),
        "novidade": inf.heaps(c), "modelos_I_de_W": modelos, "controles": nulos, "componentes_grandes": cg,
        "grau": inf.distribuicao_de_grau(dados), "compressibilidade": comp,
        "w_sq_por_coluna_final": inf.trabalho(dados, dados.n_brutas)[0] / max(1, c[-1]["colunas_nucleo"]),
        "curva": [{k: p[k] for k in ("t", "w_sq", "linhas_nucleo", "colunas_nucleo", "excesso", "ideais_vistos")} for p in c],
    }
    material = {"id": resultado["id"], "digitos": resultado["digitos"], "conjunto": conjunto, "x": caract, "nomes": nomes, "dest": dest}
    return resultado, material


def transferencia(materiais):
    """AUC de 'removida nos singletons' treinando em TODAS as instâncias `dev` de um tamanho e testando nas `teste` de outro."""
    por = {}
    for m in materiais:
        por.setdefault((m["conjunto"], m["digitos"]), []).append(m)
    tamanhos_dev = sorted({d for (c, d) in por if c == "dev"})
    tamanhos_teste = sorted({d for (c, d) in por if c == "teste"})
    saida = []
    for a in tamanhos_dev:
        treino = por[("dev", a)]
        x = np.vstack([m["x"] for m in treino])
        y = np.concatenate([m["dest"] == 1 for m in treino])
        modelo = inf.ajustar_logistica(x, y, RIDGE)
        for b in tamanhos_teste:
            aucs, solo, ops = [], [], []
            for m in por[("teste", b)]:
                e = inf.prever_logistica(modelo, m["x"])
                aucs.append(inf.auc(e, m["dest"] == 1))
                solo.append(inf.auc(m["x"][:, m["nomes"].index("maior_primo_lado1")], m["dest"] == 1))
                ops.append(inf.ponto_de_operacao(e, m["dest"] == 1, m["dest"] == 4, RECALL_UTIL))
            saida.append({"treino_digitos": a, "teste_digitos": b, "n_teste": len(aucs), "auc_logistica": float(np.mean(aucs)),
                          "auc_maior_primo_lado1": float(np.mean(solo)),
                          "fracao_rejeitada": float(np.mean([o["fracao_rejeitada"] for o in ops if o])),
                          "precisao_da_rejeicao": float(np.mean([o["precisao_da_rejeicao"] for o in ops if o])),
                          "descartaveis_pegos": float(np.mean([o["descartaveis_pegos"] for o in ops if o]))})
    return saida


# t de Student bilateral a 95% por graus de liberdade (1 a 30); acima disso, a aproximação normal corrigida
_T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110,
         2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def inclinacao(pares):
    """Inclinação (por dígito) de `y` contra os dígitos por mínimos quadrados e intervalo t de 95%.

    Medido (60 a 300 simulações com 9 a 16 pontos): o intervalo t cobre 92% a 94% e o bootstrap percentílico só 86% a 90%,
    por isso o t. Supõe ruído aproximadamente normal e independente entre instâncias; com poucos pontos é indicativo, não prova.
    """
    pares = [(d, y) for d, y in pares if d is not None and y is not None]
    if len({d for d, _ in pares}) < 3 or len(pares) < 4:
        return None
    x, y = np.array([p[0] for p in pares], dtype=float), np.array([p[1] for p in pares], dtype=float)
    n = len(x)
    a, b = np.polyfit(x, y, 1)
    res = y - (a * x + b)
    erro = float(np.sqrt((res @ res) / (n - 2) / ((x - x.mean()) ** 2).sum()))
    t = _T975[n - 3] if n - 2 <= len(_T975) else 1.96 * (1 + 2.4 / (n - 2))
    return {"inclinacao_por_digito": float(a), "ic95": [float(a - t * erro), float(a + t * erro)], "n": n}


def agregar(instancias):
    """Por conjunto e tamanho: médias das métricas escalares; e a inclinação (E6) por conjunto."""
    escalares = {
        "emergencia_fracao": lambda r: r["parada"]["emergencia"]["fracao_das_brutas"] if r["parada"]["emergencia"] else None,
        "t_min_fracao": lambda r: r["parada"]["t_min"]["fracao_das_brutas"] if r["parada"]["t_min"] else None,
        "margem_de_parada": lambda r: r["parada"]["margem_de_parada"],
        "fracao_duplicatas": lambda r: r["fracao_duplicatas"],
        "fracao_removida_nos_singletons": lambda r: r["destinos_das_unicas"]["unica_removida_nos_singletons"],
        "fracao_cortada_pelos_cliques": lambda r: r["destinos_das_unicas"]["nucleo_cortada_pelos_cliques"],
        "fracao_na_matriz": lambda r: r["destinos_das_unicas"]["na_matriz"],
        "beta_de_heaps": lambda r: r["novidade"]["beta"],
        "excesso_final_sobre_linhas": lambda r: r["curva"][-1]["excesso"] / max(1, r["curva"][-1]["linhas_nucleo"]),
        "excesso_real_menos_configuracao": lambda r: (r["controles"]["real"]["excesso_final"] - r["controles"]["configuracao"]["excesso_final"])
        / max(1, r["controles"]["real"]["linhas_nucleo_final"]),
        "w_sq_por_coluna_final": lambda r: r["w_sq_por_coluna_final"],
    }
    tabela, incl = {}, {}
    for conjunto in sorted({r["conjunto"] for r in instancias}):
        rs = [r for r in instancias if r["conjunto"] == conjunto]
        for nome, f in escalares.items():
            vals = {}
            for r in rs:
                v = f(r)
                if v is not None:
                    vals.setdefault(r["digitos"], []).append(float(v))
            tabela.setdefault(conjunto, {})[nome] = {str(d): {"media": float(np.mean(v)), "dp": float(np.std(v)), "n": len(v)}
                                                    for d, v in sorted(vals.items())}
            incl.setdefault(conjunto, {})[nome] = inclinacao([(r["digitos"], f(r)) for r in rs])
    return {"por_tamanho": tabela, "inclinacao": incl}


def _instancia_com_cache(pasta, conjunto, cache):
    """`analisar_instancia` com ponto de retomada por instância (o job é longo e o contêiner reinicia).

    A chave é o hash do código do pipeline e do manifesto da captura: mudou um dos dois, recalcula. Não altera nenhuma métrica.
    """
    if not cache:
        return analisar_instancia(pasta, conjunto)
    import hashlib
    import pickle
    h = hashlib.sha256()
    for f in (__file__, rel.__file__, inf.__file__, str(Path(pasta) / "manifest.json")):
        h.update(Path(f).read_bytes())
    h.update(conjunto.encode())
    arq = Path(cache) / f"{Path(pasta).name}-{conjunto}-{h.hexdigest()[:16]}.pkl"
    if arq.is_file():
        return pickle.loads(arq.read_bytes())
    r = analisar_instancia(pasta, conjunto)
    Path(cache).mkdir(parents=True, exist_ok=True)
    arq.write_bytes(pickle.dumps(r))
    return r


def analisar(saida, dev, teste, cache=None):
    instancias, materiais = [], []
    for conjunto, pastas in (("dev", dev), ("teste", teste)):
        for p in pastas:
            r, m = _instancia_com_cache(p, conjunto, cache)
            instancias.append(r)
            materiais.append(m)
            print(conjunto, r["id"], "valida o purge:", r["valida_o_purge_do_cado"], flush=True)
    resultado = {"formato": "baseline-informacao/v1", "parametros": {
        "pontos": PONTOS, "pontos_nulo": PONTOS_NULO, "sementes_nulo": list(SEMENTES_NULO), "manter": MANTER, "ridge": RIDGE,
        "recall_util": RECALL_UTIL, "amostra_compressao": AMOSTRA_COMPRESSAO},
        "instancias": instancias, "transferencia": transferencia(materiais), "agregado": agregar(instancias)}
    Path(saida).write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
    return resultado


def veredictos(res):
    """P1-P5 de docs/fatoracao/predicoes-informacao.md, avaliadas só nas instâncias `teste` (as de `dev` se não houver teste)."""
    inst = [r for r in res["instancias"] if r["conjunto"] == "teste"] or res["instancias"]
    conj = inst[0]["conjunto"] if inst else None
    fora = [r["id"] for r in inst if not r["parada"]["emergencia"] or not 0.5 <= r["parada"]["emergencia"]["fracao_das_brutas"] <= 0.85]
    m5 = [r["modelos_I_de_W"]["excesso"]["vencedor"].startswith("M5") for r in inst]
    id_ok = [r["modelos_I_de_W"]["ideais_vistos"]["vencedor"][:2] in ("M2", "M3") for r in inst]
    largas = [r["id"] for r in inst if r["parada"]["margem_de_parada"] is None or r["parada"]["margem_de_parada"] > 0.15]
    inc = (res["agregado"]["inclinacao"].get(conj, {}) or {}).get("margem_de_parada")
    tr = [t for t in res["transferencia"] if t["treino_digitos"] < t["teste_digitos"]]
    ruins_p4 = [(t["treino_digitos"], t["teste_digitos"]) for t in tr if t["auc_logistica"] < 0.75 or t["fracao_rejeitada"] > 0.15]
    pior = [r["id"] for r in inst if r["controles"]["real"]["excesso_final"] >= r["controles"]["configuracao"]["excesso_final"]]
    dif = [abs(r["compressibilidade"]["real"]["bits_por_relacao"] / r["compressibilidade"]["configuracao"]["bits_por_relacao"] - 1) for r in inst]
    return {
        "conjunto": conj, "n": len(inst),
        "P1": {"passa": len(fora) <= 1, "fora_de_0.5_0.85": fora},
        "P2": {"passa": bool(m5) and np.mean(m5) >= 0.9 and all(id_ok), "frac_M5_no_excesso": float(np.mean(m5)) if m5 else None,
               "ideais_vistos_M2_ou_M3_em_todas": all(id_ok)},
        "P3": {"passa": len(largas) <= 1, "margem_acima_de_15pct": largas, "inclinacao_da_margem": inc},
        "P4": {"passa": (not ruins_p4) if tr else None, "pares_reprovados": ruins_p4, "n_pares": len(tr)},
        "P5": {"passa": not pior and bool(dif) and max(dif) < 0.10, "excesso_real_nao_menor_que_o_nulo": pior,
               "maior_diferenca_de_compressibilidade": max(dif) if dif else None},
    }


def relatorio(res):
    """Markdown do resultado: tudo vem do JSON, nada é digitado."""
    f = lambda x, n=3: "n/d" if x is None else f"{x:.{n}f}"  # noqa: E731
    out = ["| id | conj | brutas | duplicatas | na matriz | cortada pelos cliques | removida nos singletons | emergência | t_min | margem | I(W): excesso / ideais |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["instancias"]:
        d, p = r["destinos_das_unicas"], r["parada"]
        out.append(f"| {r['id']} | {r['conjunto']} | {r['n_brutas']} | {f(r['fracao_duplicatas'])} | {f(d['na_matriz'])} | "
                   f"{f(d['nucleo_cortada_pelos_cliques'])} | {f(d['unica_removida_nos_singletons'])} | "
                   f"{f(p['emergencia']['fracao_das_brutas'] if p['emergencia'] else None)} | "
                   f"{f(p['t_min']['fracao_das_brutas'] if p['t_min'] else None)} | {f(p['margem_de_parada'])} | "
                   f"{r['modelos_I_de_W']['excesso']['vencedor'][:2]} / {r['modelos_I_de_W']['ideais_vistos']['vencedor'][:2]} |")
    out += ["", "| treino (dígitos) | teste (dígitos) | n | AUC logística | AUC só maior primo | fração rejeitada a 99% de recall | precisão da rejeição |",
            "|---|---|---|---|---|---|---|"]
    for t in res["transferencia"]:
        out.append(f"| {t['treino_digitos']} | {t['teste_digitos']} | {t['n_teste']} | {f(t['auc_logistica'])} | {f(t['auc_maior_primo_lado1'])} | "
                   f"{f(t['fracao_rejeitada'])} | {f(t['precisao_da_rejeicao'])} |")
    teste = [r for r in res["instancias"] if r["conjunto"] == "teste"] or res["instancias"]
    out += ["", "| dígitos | n | bits/relação real | configuração | ordem embaralhada | gzip real | emergência real | emergência configuração | excesso final real | configuração | β de Heaps | ideais novos por relação no fim |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for dig in sorted({r["digitos"] for r in teste}):
        rs = [r for r in teste if r["digitos"] == dig]
        m = lambda g: float(np.mean([g(r) for r in rs]))  # noqa: E731
        out.append(f"| {dig} | {len(rs)} | {m(lambda r: r['compressibilidade']['real']['bits_por_relacao']):.1f} | "
                   f"{m(lambda r: r['compressibilidade']['configuracao']['bits_por_relacao']):.1f} | "
                   f"{m(lambda r: r['compressibilidade']['ordem']['bits_por_relacao']):.1f} | "
                   f"{m(lambda r: r['compressibilidade']['real']['compressores']['gzip']):.3f} | "
                   f"{m(lambda r: r['parada']['emergencia']['fracao_das_brutas']):.3f} | "
                   f"{m(lambda r: r['controles']['configuracao']['emergencia_fracao']):.3f} | "
                   f"{m(lambda r: r['controles']['real']['excesso_final']):.0f} | "
                   f"{m(lambda r: r['controles']['configuracao']['excesso_final']):.0f} | "
                   f"{m(lambda r: r['novidade']['beta']):.3f} | "
                   f"{m(lambda r: r['novidade']['ideais_novos_por_relacao_no_ultimo_trecho']):.3f} |")
    incl = (res["agregado"]["inclinacao"].get(teste[0]["conjunto"]) or {}) if teste else {}
    out += ["", "| métrica | inclinação por dígito | IC 95% | n |", "|---|---|---|---|"]
    for nome, v in sorted(incl.items()):
        if v:
            out.append(f"| {nome} | {v['inclinacao_por_digito']:+.4f} | [{v['ic95'][0]:+.4f}, {v['ic95'][1]:+.4f}] | {v['n']} |")
    v = veredictos(res)
    out += ["", f"Veredictos (conjunto `{v['conjunto']}`, {v['n']} instâncias):", ""]
    for k in ("P1", "P2", "P3", "P4", "P5"):
        out.append(f"- **{k}: {'sem dado' if v[k]['passa'] is None else 'passou' if v[k]['passa'] else 'FALHOU'}** — {json.dumps({a: b for a, b in v[k].items() if a != 'passa'}, ensure_ascii=False)}")
    return "\n".join(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) >= 2 and argv[0] == "analisar":
        def pegar(flag):
            if flag not in argv:
                return []
            i = argv.index(flag) + 1
            out = []
            while i < len(argv) and not argv[i].startswith("--"):
                out.append(argv[i])
                i += 1
            return out
        cache = (pegar("--cache") or [None])[0]
        analisar(argv[1], pegar("--dev"), pegar("--teste"), cache)
        return 0
    if len(argv) == 2 and argv[0] == "relatorio":
        print(relatorio(json.loads(Path(argv[1]).read_text(encoding="utf-8"))))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
