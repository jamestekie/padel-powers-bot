import json,re
from collections import Counter,defaultdict
R=json.load(open('work/rows.json'))
for x in R:
    x['akt_sub']=x['qcat'] if x['tcat']=='AKT' else None
    if x['tcat']=='AKT': x['qcat']='AKT'
reg=[x for x in R if x['regular']]
nq=len({x['qid'] for x in reg}); print('regular quizzes',nq,'questions',len(reg), 'dates',min(x['date'] for x in reg),max(x['date'] for x in reg))
avg=lambda l: sum(l)/len(l) if l else float('nan')
print('\n== celkova prumerna uspesnost (exp bodu/otazka):',round(avg([x['exp'] for x in reg if x['exp'] is not None]),3))
print('\n== kategorie otazek (regular): n, na kviz, podil, prum. uspesnost, ztrata bodu/kviz prumerneho tymu, podil tezkych(<35%)')
c=defaultdict(list)
for x in reg: c[x['qcat']].append(x)
for k,v in sorted(c.items(),key=lambda kv:-len(kv[1])):
    e=[x['exp'] for x in v if x['exp'] is not None]
    print(f"{k:4} {len(v):5} {len(v)/nq:5.1f} {100*len(v)/len(reg):5.1f}% {100*avg(e):5.1f}% {len(v)/nq*(1-avg(e)):5.2f} {100*sum(1 for y in e if y<.35)/len(e):5.1f}%")
print('\n== hlavni kategorie temat podle pozice (regular)')
pos=defaultdict(Counter)
for x in reg:
    if x['n']%5==1: pos[x['pos']][x['tcat']]+=1
for p in sorted(pos): print(p,sum(pos[p].values()),pos[p].most_common(9))
print('\n== uspesnost podle pozice tematu')
for p in sorted(pos):
    e=[x['exp'] for x in reg if x['pos']==p and x['exp'] is not None]; print(p,round(100*avg(e),1))
print('\n== formaty (regular): podil, uspesnost')
for f in ['abcd','prirazovani','poslech','obrazek','iknow']:
    v=[x for x in reg if f in x['fmt']]; e=[x['exp'] for x in v if x['exp'] is not None]
    print(f,len(v),round(100*len(v)/len(reg),1),round(100*avg(e),1), 'na kviz',round(len(v)/nq,1))
hp=[x for x in reg if x['p05'] is not None]; print('pulbodove otazky',len(hp),round(100*len(hp)/len([x for x in reg if x['p1'] is not None]),1))
print('\n== podoblasti aktualit (kde je rozepsano)')
print(Counter(x['akt_sub'] for x in reg if x['akt_sub'] and x['akt_sub']!='AKT').most_common())
print('\n== rekonstruovatelnost facts', Counter(x['fact'] for x in R))
print('\n== temata tcat count (regular)'); print(Counter(x['tcat'] for x in reg if x['n']%5==1).most_common())
print('\n== iKNOW kvizu:',len({x['qid'] for x in reg if x['tcat']=='IKN'}), 'kvizu se 45 otazkami', sum(1 for q,n in Counter(x['qid'] for x in reg).items() if n==45))
# recurring answers
def norm(a):
    a=re.sub(r'\(.*?\)','',a.lower()); a=re.sub(r'^(v |ve |na |z |ze |o |do |u |k )','',a.strip()); return a.strip(' .')
ans=Counter()
for x in R:
    if 'abcd' in x['fmt'] or 'prirazovani' in x['fmt']: continue
    for part in re.split(r'[;,/]| a ',x['a']):
        n=norm(part)
        if len(n)>3 and not re.fullmatch(r'[\d\s.]+',n): ans[n]+=1
print('\n== nejcastejsi odpovedi'); print(ans.most_common(70))
