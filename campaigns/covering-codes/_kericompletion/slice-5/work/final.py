import json,re,glob,os
cells=json.load(open('/home/user/Matematica/ledger/cells.json'))['cells']
d={x['id']:x for x in cells}
fat=json.load(open('../fatias.json'))['fatias'][5]
runs={}
for f in ['work/run.log','work/run2.log','work/run3.log']:
    if not os.path.exists(f): continue
    cur=None
    for l in open(f):
        m=re.match(r'== (K\S+) M=(\d+)',l)
        if m: cur=m.group(1); continue
        m=re.match(r'q=(\d+) n=(\d+) R=(\d+) M=(\d+) seed=(\d+) iters=(\d+) best_unc=(\d+) final_unc=(\d+) t=(\d+)s',l)
        if m and cur:
            g=list(map(int,m.groups()))
            runs.setdefault(cur,[]).append(dict(comando=f"work/sa {g[0]} {g[1]} {g[2]} {g[3]} <tempo> {g[4]} <saida> 1 0.2",M_alvo=g[3],semente=g[4],iteracoes=g[5],melhor_descobertos=g[6],finais=g[7],segundos=g[8],achou=g[6]==0))
res=[];
for i in fat:
    p=d[i]['published']; r=runs.get(i,[])
    res.append(dict(id=i,ub_publicada=p['ub']['value'],fonte=p['ub']['source'],lb_publicada=p['lb']['value'],melhor_nosso_verificado_ou_null=None,M=None,sha256=None,verificadores_PASS=[],tentativas=r,estado='SEM_MELHORA_NESTA_BUSCA' if r else 'NAO_TENTADA'))
json.dump(res,open('resultados.json','w'),indent=1,ensure_ascii=False)
L=["# Fatia 5 — relatório (covering codes K_q(n,R))","",
"Método: SA genérico em C (`work/sa.c`, move uma coordenada de uma palavra, metade guiada por ponto descoberto, T 1.0→0.2), alvo M = ub_publicada−1, 1 núcleo, 1 semente. Calibração: K2(11,2) com M=50 achou cobertura em 3 s (SA funciona), mas em M=ub−1 nenhuma célula chegou a 0 descobertos.","",
"Nenhum código menor que a cota da tabela consultada foi encontrado; nenhuma célula foi fechada (não houve busca exata ILP/SAT: espaços de 16 mil a 8 milhões de pontos tornam o ILP direto inviável no orçamento). Resultado negativo desta busca curta, não prova de inexistência.","",
"| célula | ub tabela (fonte) | lb | M tentado | melhor nº de pontos descobertos | s | estado |","|---|---|---|---|---|---|---|"]
for x in res:
    t=x['tentativas']
    if t: b=min(t,key=lambda a:a['melhor_descobertos']); L.append(f"| {x['id']} | {x['ub_publicada']} ({x['fonte']}) | {x['lb_publicada']} | {b['M_alvo']} | {b['melhor_descobertos']} | {b['segundos']} | {x['estado']} |")
    else: L.append(f"| {x['id']} | {x['ub_publicada']} ({x['fonte']}) | {x['lb_publicada']} | - | - | - | NAO_TENTADA |")
L+=["","Tempo: 190 s por célula nas três primeiras (K7(5,3), K2(11,2), K2(12,3)), 45 a 61 s nas demais (sessão interrompida no meio; tempos curtos, 1 semente). Verificadores (C oficial e verify.py) não foram usados porque nenhum código foi achado. Nada fora de slice-5/ foi alterado.",""]
open('RELATORIO.md','w').write("\n".join(L))
