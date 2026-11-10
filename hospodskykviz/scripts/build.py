import json,glob,re,csv,sys
from collections import Counter,defaultdict
ds=json.load(open('work/dataset.json'))
lab={}
for f in glob.glob('work/labels*.jsonl'):
    for l in open(f):
        l=l.strip()
        if l: j=json.loads(l); lab[j['tid']]=j
# fill difficulty from vp2
extra={}
for f in glob.glob('data/vp2_[0-9a-f]*.json'):
    d=json.load(open(f)); extra[(d['rows'][0]['q'],d['rows'][1]['q'])]=d['rows']
def fmt(q,a):
    f=[]
    ql=q.lower()
    if re.fullmatch(r'[A-Da-d]\)?',a.strip()) or re.match(r'[A-D]\)\s*\S',a.strip()) or re.match(r'[A-D] \(',a.strip()): f.append('abcd')
    if re.fullmatch(r'(\d\s*[A-Da-d][\s;,]*){3,}',a.strip()): f.append('prirazovani')
    if re.search(r'ukáz|uslyš|poslech|zazní|poslouch|písničk|píseň|skladb|nazpív',ql): f.append('poslech')
    if re.search(r'obráz|fot|vidíte|vidíme|vyobraz|snímk|grafi|mapě|mapa|logo|plakát|obálk',ql): f.append('obrazek')
    if ql.startswith('poznejte ') and len(q)<32 and not q.endswith('...'): f.append('iknow')
    return f
rows=[]
for q in ds:
    k=None
    for t in q['themes']:
        L=lab.get(t['tid'],{})
        for i,r in enumerate(t['rows']):
            rows.append(dict(qid=q['qid'],date=q['date'],pub=q['pub'],tid=t['tid'],pos=t['pos'],n=int(r['n'].strip('.')),
                tname=L.get('name',''),tcat=L.get('cat',''),sub=L.get('sub',''),qcat=(L.get('q') or ['']*9)[i] if L else '',
                fact=(L.get('facts') or [None]*9)[i] if L else None,q=r['q'],a=r['a'],p1=r.get('p1'),p05=r.get('p05'),fmt=fmt(r['q'],r['a'])))
    ex=extra.get((q['themes'][0]['rows'][0]['q'],q['themes'][0]['rows'][1]['q']))
    if ex:
        mine=[x for x in rows if x['qid']==q['qid']]
        for x,r in zip(mine,ex):
            if x['q']==r['q'] and r.get('diff'):
                m=re.search(r'za 1 bod ([\d.]+) %',r['diff']); x['p1']=float(m.group(1)) if m else None
                m=re.search(r'za 0\.5 bodu ([\d.]+) %',r['diff']); x['p05']=float(m.group(1)) if m else None
# regular weekly quiz = first theme is AKT
reg={q['qid']: lab.get(q['themes'][0]['tid'],{}).get('cat')=='AKT' for q in ds}
for x in rows:
    x['regular']=reg[x['qid']]
    x['exp']=None if x['p1'] is None else (x['p1']+0.5*(x['p05'] or 0))/100
# drop near-duplicate quizzes (same week, other venue): keep the one with difficulty / earlier in list
from collections import defaultdict as _dd
byq=_dd(list)
for x in rows: byq[x['qid']].append(x)
keep=[];drop=set()
order=sorted(byq,key=lambda q:(sum(1 for x in byq[q] if x['p1'] is None),q))
for q in order:
    s_=set((x['q'],x['a']) for x in byq[q])
    if any(len(s_&k)>=20 for k in keep): drop.add(q)
    else: keep.append(s_)
print('dropped duplicate quizzes',len(drop))
rows=[x for x in rows if x['qid'] not in drop]
json.dump(rows,open('work/rows.json','w'),ensure_ascii=False)
print(len(rows),'rows; labeled',sum(1 for x in rows if x['qcat']),'; with difficulty',sum(1 for x in rows if x['p1'] is not None),'; regular quizzes',sum(reg.values()),'of',len(reg))
print('non-regular:',[(q['date'],q['pub'],lab.get(q['themes'][0]['tid'],{}).get('name')) for q in ds if not reg[q['qid']]])
