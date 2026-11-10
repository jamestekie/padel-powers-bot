import json,csv,os,sys
from collections import defaultdict
out=sys.argv[1]; os.makedirs(out+'/data',exist_ok=True)
R=json.load(open('work/rows.json'))
NAMES={'AKT':'Aktuality','HIS':'Historie','GEO':'Zeměpis','PRI':'Příroda','VED':'Věda a technika','FIL':'Film a seriály','HUD':'Hudba','LIT':'Literatura a jazyk','UME':'Umění a kultura','SPO':'Sport','GAS':'Gastronomie','SPL':'Společnost','HRY':'Hry a popkultura','SLO':'Slovní hříčky a logika','IKN':'iKNOW','MIX':'Všehochuť'}
with open(out+'/data/otazky.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['datum','podnik','bezny_tydenni_kviz','cislo_otazky','cislo_tematu','tema','kategorie_tematu','podoblast','kategorie_otazky','zacatek_otazky','spravna_odpoved','uspesnost_1b_pct','uspesnost_05b_pct','format','rekonstruovatelnost_0_2'])
    for x in R: w.writerow([x['date'],x['pub'],int(x['regular']),x['n'],x['pos'],x['tname'],x['tcat'],x['sub'],x['qcat'],x['q'],x['a'],x['p1'],x['p05'],' '.join(x['fmt']),x['fact']])
T=defaultdict(list)
for x in R: T[x['tid']].append(x)
rows=[]
for tid,v in T.items():
    e=[x['exp'] for x in v if x['exp'] is not None]
    rows.append([v[0]['date'],v[0]['pub'],int(v[0]['regular']),v[0]['pos'],v[0]['tname'],v[0]['tcat'],v[0]['sub'],round(100*sum(e)/len(e),1) if e else '',' | '.join(x['a'] for x in v)])
rows.sort()
with open(out+'/data/temata.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['datum','podnik','bezny_tydenni_kviz','cislo_tematu','tema','kategorie','podoblast','prumerna_uspesnost_pct','odpovedi']); w.writerows(rows)
# theme catalogue markdown
with open(out+'/KATALOG_TEMAT.md','w',encoding='utf-8') as f:
    f.write('# Katalog témat podle kategorií\n\nVšechna témata z běžných týdenních kvízů. Číslo v závorce je průměrná celostátní úspěšnost tématu v procentech. Seřazeno od nejtěžších.\n')
    cat=defaultdict(list)
    for r in rows:
        if r[2]: cat[r[5]].append(r)
    for k in ['AKT','FIL','HUD','SPL','PRI','GEO','HIS','SPO','GAS','VED','LIT','UME','HRY','SLO','MIX','IKN']:
        if k=='AKT': continue
        f.write(f"\n## {NAMES[k]} ({len(cat[k])} témat)\n\n| Téma | Podoblast | Úspěšnost | Datum | Odpovědi |\n|---|---|---|---|---|\n")
        for r in sorted(cat[k],key=lambda r:(r[7]=='',r[7])): f.write(f"| {r[4]} | {r[6]} | {r[7]} | {r[0]} | {r[8].replace('|','·')} |\n")
print('ok',len(R),len(rows))
