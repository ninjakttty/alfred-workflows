import json
from pathlib import Path
countries={}
for line in open('/usr/share/zoneinfo/iso3166.tab'):
 if not line.startswith('#') and '\t' in line:
  k,v=line.strip().split('\t',1);countries[k]=v
rows=[]
for line in open('/usr/share/zoneinfo/zone.tab'):
 if line.startswith('#') or not line.strip():continue
 p=line.strip().split('\t'); z=p[2];city=z.split('/')[-1].replace('_',' ')
 rows.append(dict(city=city,country=countries.get(p[0],p[0]),countryCode=p[0],zone=z,aliases=z.replace('_',' ')))
extra=[('San Francisco','United States','America/Los_Angeles','sf san fran california usa us'),('Seattle','United States','America/Los_Angeles','washington usa us'),('Washington DC','United States','America/New_York','washington dc usa us'),('Boston','United States','America/New_York','massachusetts usa us'),('Las Vegas','United States','America/Los_Angeles','nevada usa us'),('Mumbai','India','Asia/Kolkata','bombay'),('New Delhi','India','Asia/Kolkata','delhi'),('Beijing','China','Asia/Shanghai','peking'),('Manchester','United Kingdom','Europe/London','uk britain england'),('Frankfurt','Germany','Europe/Berlin',''),('Munich','Germany','Europe/Berlin','munchen münchen'),('Kyiv','Ukraine','Europe/Kiev','kiev'),('UTC','Universal','UTC','gmt')]
codes={name:code for code,name in countries.items()}
codes["United Kingdom"]="GB"
for city,country,zone,aliases in extra:rows.append(dict(city=city,country=country,countryCode=codes.get(country),zone=zone,aliases=aliases))
for r in rows:
 if r['country']=='United States':r['aliases']+=' usa us'
 if r['country']=='United Kingdom':r['aliases']+=' uk britain'
 if r['city']=='Kolkata':r['aliases']+=' calcutta'
json.dump(rows,open(Path(__file__).resolve().parents[1] / 'workflow/cities.json','w'),ensure_ascii=False)
print(len(rows),'cities')
