import json,glob,re,os,subprocess
c={x['id']:x for x in json.load(open('../../../../ledger/cells.json'))['cells']}
f=json.load(open('../fatias.json'))['fatias'][6]
rows=[]
for i in f:
    m=re.match(r'K(\d+)\((\d+),(\d+)\)',i);q,n,R=map(int,m.groups())
    ub=c[i]['published']['ub'];lb=c[i]['published']['lb']['value']
    log=f'work/log_q{q}_n{n}_R{R}.txt'
    t=[];best=None
    if os.path.exists(log):
        for l in open(log):
            if 'best_unc' in l:
                t.append(l.strip());b=int(re.search(r'best_unc=(\d+)',l).group(1));best=b if best is None else min(best,b)
            elif l.startswith('cmd:'): t.append(l.strip())
    found=glob.glob(f'work/found_q{q}_n{n}_R{R}_*.txt')
    est='SEM_MELHORA_NESTA_BUSCA' if t else 'NAO_TENTADA'
    r=dict(id=i,ub_publicada=ub['value'],lb_publicada=lb,fonte=ub['source'],melhor_nosso_verificado_ou_null=None,M=None,sha256=None,verificadores_PASS=[],
      tentativas=t,melhor_descobertos_min=best,estado=est)
    if found:
        r['achado_nao_verificado_arquivos']=found
    rows.append(r)
json.dump(rows,open('resultados.json','w'),indent=1,ensure_ascii=False)
L=['# Fatia 6: relatório (busca parcial, recozimento simulado)\n',
'Método: `work/sa.c` (recozimento simulado de M palavras, custo = pontos descobertos, delta exato por troca de um dígito), 1 núcleo, `nice -n 10`, alvo M = ub_publicada - 1. Cada célula: 2 execuções curtas (seeds 11 e 12, ciclos térmicos 3; T 0.35->0.15 e 0.25->0.10). Células K2(11,1), K2(12,2) e parte de K5(6,2): 110 s por execução; as demais: 50 s.\n',
'Nenhum código com M menor que a cota da tabela consultada foi encontrado nesta busca; nenhuma célula foi fechada. Não é afirmação de inexistência. Limitações: o SA não foi calibrado (sanidade: K2(11,1) com M=200 cobriu; com M=191 ficou em 6 pontos descobertos), e os limites inferiores não foram tocados. Sem verificadores rodados, pois nada a verificar.\n',
'| célula | lb | ub tabela (fonte) | M tentado | menor nº de pontos descobertos | estado |','|---|---|---|---|---|---|']
for r in rows:
    L.append(f"| {r['id']} | {r['lb_publicada']} | {r['ub_publicada']} ({r['fonte']}) | {r['ub_publicada']-1} | {r['melhor_descobertos_min']} | {r['estado']} |")
L.append('\nComandos/logs: `work/log_*.txt`, driver `work/run.sh`/`work/run2.sh`.')
open('RELATORIO.md','w').write('\n'.join(L)+'\n')
