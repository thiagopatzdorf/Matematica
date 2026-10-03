import sys,re,subprocess,time
def q(s,n=15):
    for tr in range(3):
        r=subprocess.run(['curl','-sS','-m','40','-G','https://export.arxiv.org/api/query','--data-urlencode','search_query='+s,'--data-urlencode','sortBy=submittedDate','--data-urlencode','sortOrder=descending','--data-urlencode','max_results=%d'%n],capture_output=True,text=True)
        if '<entry>' in r.stdout or '<feed' in r.stdout and 'totalResults>0' in r.stdout.replace(' ',''): return r.stdout
        time.sleep(5)
    return r.stdout
for s in sys.argv[1:]:
    t=q(s); print('==',s)
    for e in t.split('<entry>')[1:]:
        g=lambda k: re.search('<%s>(.*?)</%s>'%(k,k),e,re.S).group(1).strip().replace('\n',' ')
        print(re.search('<published>(.*?)</published>',e).group(1)[:10], re.search('<id>.*abs/(.*?)</id>',e).group(1), g('title')[:110])
    time.sleep(3)
