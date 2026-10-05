import json,re,os,subprocess,hashlib
root=os.path.dirname(os.path.abspath(__file__))+'/..'
cells={x['id']:x for x in json.load(open('/home/user/Matematica/ledger/cells.json'))['cells']}
ids=json.load(open('/home/user/Matematica/campaigns/covering-codes/_kericompletion/fatias.json'))['fatias'][0]
log=open(root+'/work/sa_log.txt').read()
res=[]
for i in ids:
    c=cells[i];p=c['published'];ub=p['ub']['value'];lb=p['lb']['value']
    m=re.search(re.escape('== '+i+' ')+r'M=(\d+) secs=(\d+) seed=1 cmd: (.*?)\n(q=.*?)\n(FOUND|NO best=\d+)',log)
    tent=[]
    if m:
        tent.append({"metodo":"SA generico (work/sa.c), M fixo, minimiza descobertos","M_alvo":int(m.group(1)),"cmd":m.group(3),"semente":1,"segundos_cpu":int(m.group(2)),"saida":m.group(4),"resultado":m.group(5)})
    if i=='K3(7,3)':
        tent.append({"metodo":"ILP exato HiGHS via scipy (work/ilp.py), restricao M<=11","cmd":"python3 ilp.py 3 7 3 240 11","resultado":"limite de tempo 240s sem solucao viavel e sem cota dual: nada provado"})
    found=m and m.group(5)=='FOUND'
    r={"id":i,"ub_publicada":ub,"lb_publicada":lb,"fonte":p['ub']['source'],"melhor_nosso_verificado_ou_null":None,"M":None,"sha256":None,"verificadores_PASS":[],"tentativas":tent,"estado":"SEM_MELHORA_NESTA_BUSCA" if m else "NAO_TENTADA"}
    if found:
        r["estado"]="ACHADO_PENDENTE_VERIFICACAO"
    res.append(r)
json.dump(res,open(root+'/resultados.json','w'),indent=1,ensure_ascii=False)
print(json.dumps([(r['id'],r['estado'],[t.get('saida','')[-40:] for t in r['tentativas']]) for r in res],indent=0))
