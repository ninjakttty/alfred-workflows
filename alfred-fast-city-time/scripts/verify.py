import subprocess,json,time,statistics,os,datetime,zoneinfo,pathlib
project=pathlib.Path(__file__).resolve().parents[1]
root=project/'workflow'
build=project/'.build'
build.mkdir(exist_ok=True)
env=dict(os.environ,alfred_workflow_cache=str(build/'test-cache'),TZ='Europe/Dublin')
def run(q=''):
 return json.loads(subprocess.check_output(['/bin/zsh','-f','run.zsh',q],cwd=root,env=env))
t=time.perf_counter();fav=run();first=(time.perf_counter()-t)*1000
assert [i['title'].split('  ·  ')[0] for i in fav['items']]==['San Francisco','Dublin','Berlin']
for q,expected in [('TOKYO','Tokyo'),('san fran','San Francisco'),('sf','San Francisco'),('münchen','Munich'),('berlin','Berlin')]:
 assert any(i['title'].startswith(expected) for i in run(q)['items']),q
assert len(run('united states')['items'])>5
assert run('zzzznonexistent')['items'][0]['valid']==False
for name,z in [('San Francisco','America/Los_Angeles'),('Dublin','Europe/Dublin'),('Berlin','Europe/Berlin'),('Kathmandu','Asia/Kathmandu')]:
 item=next(i for i in run(name)['items'] if i['title'].startswith(name))
 now=datetime.datetime.now(zoneinfo.ZoneInfo(z)); expected=now.strftime('%I:%M %p').lstrip('0')
 assert item['arg']==expected,(name,item,expected)
samples=[]
for n in range(60):
 t=time.perf_counter();run(['','berlin','united states','tokyo'][n%4]);samples.append((time.perf_counter()-t)*1000)
report={'first_cache_setup_ms':round(first,1),'runs':len(samples),'median_ms':round(statistics.median(samples),1),'p95_ms':round(sorted(samples)[int(len(samples)*.95)-1],1),'max_ms':round(max(samples),1),'checks':'Favourites, aliases, case/accent folding, country search, no matches, current times including fractional offset; wrapper and native startup included. Alfred UI rendering excluded.'}
print(json.dumps(report,indent=2));(build/'benchmark.json').write_text(json.dumps(report,indent=2))
