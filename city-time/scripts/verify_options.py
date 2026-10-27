#!/usr/bin/env python3
"""Verify time-format settings and favourites management without changing Alfred preferences."""
import datetime,json,os,pathlib,plistlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
exe=root/'.build/city-time'
base=dict(os.environ)
for key in ['use_24_hour','favourite_cities']:base.pop(key,None)
def run(query='',**options):
    return json.loads(subprocess.check_output([str(exe),query],env=dict(base,**options)))['items']
def names(items):return [x['title'].split('  ·  ')[0] for x in items]
assert names(run())==['San Francisco','Dublin','Berlin']
assert names(run(favourite_cities='Tokyo\nDublin'))==['Tokyo','Dublin']
assert all('uid' not in item for item in run())
assert all('uid' not in item for item in run(favourite_cities='Berlin\nSan Francisco\nDublin'))
assert names(run(favourite_cities='Berlin\nSan Francisco\nDublin'))==['Berlin','San Francisco','Dublin']
assert 'uid' in run('berlin')[0]
assert names(run(favourite_cities='Berlin'))==['Berlin']
assert names(run(favourite_cities=' berlin \nBerlin;Tokyo, Dublin'))==['Berlin','Tokyo','Dublin']
assert names(run(favourite_cities='San Francisco|America/Los_Angeles'))==['San Francisco']
assert run(favourite_cities='')[0]['title']=='No favourite cities'
assert run(favourite_cities='Atlantis')[0]['title']=='Unknown favourite: Atlantis'
assert run(favourite_cities='Berlin|Asia/Tokyo')[0]['valid']==False
assert names(run(favourite_cities='Berlin\nAtlantis'))[0]=='Berlin'
assert names(run('tokyo',favourite_cities=''))[0]=='Tokyo'
for value in ['1','true','TRUE','yes']:
    item=run('berlin',use_24_hour=value)[0]
    datetime.datetime.strptime(item['arg'],'%H:%M')
    assert len(item['arg'])==5
    assert item['title'].endswith(item['arg'])
    assert item['text']['copy']==item['arg']
    assert item['mods']['cmd']['arg']=='Berlin: '+item['arg']
for value in ['0','false','']:
    assert run('berlin',use_24_hour=value)[0]['arg'].endswith((' AM',' PM'))
d=plistlib.loads((root/'workflow/info.plist').read_bytes())
config={x['variable']:x for x in d['userconfigurationconfig']}
assert config['use_24_hour']['config']['default']==False
assert config['favourite_cities']['config']['default']=='San Francisco\nDublin\nBerlin'
assert d['bundleid']=='net.ninjakitty.fast-city-time'
assert d['createdby']=='Yuri Parsons'
assert d['webaddress']=='https://www.ninjakitty.net'
assert '/v7"' in (root/'workflow/run.zsh').read_text()
print('Time format, favourites add/remove/reorder/empty/invalid handling, copy output, defaults, and metadata checks passed.')
