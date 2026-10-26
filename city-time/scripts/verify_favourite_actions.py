#!/usr/bin/env python3
import json,os,pathlib,plistlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
env=dict(os.environ,favourite_cities='San Francisco\nDublin\nBerlin')
def run(query='',fav=None):
    e=dict(env)
    if fav is not None:e['favourite_cities']=fav
    return json.loads(subprocess.check_output([str(root/'.build/city-time'),query],env=e))['items']
item=run('tokyo')[0]
assert '★' not in item['title']
assert item['mods']['alt']['subtitle']=='Add Tokyo to favourites'
added=item['mods']['alt']['arg']
assert added=='San Francisco\nDublin\nBerlin\nTokyo|Asia/Tokyo'
items=run(fav=added)
assert len(items)==4 and items[-1]['title'].startswith('Tokyo  ·')
assert all('★' not in x['title'] for x in items)
assert items[-1]['mods']['alt']['subtitle']=='Remove Tokyo from favourites'
assert items[-1]['mods']['alt']['arg']==env['favourite_cities']
assert run('berlin')[0]['arg'].endswith((' AM',' PM'))
assert run('berlin')[0]['mods']['cmd']['arg'].startswith('Berlin: ')
last=run(fav='Berlin')[0]
assert last['mods']['alt']['arg']==''
assert run(fav='')[0]['title']=='No favourite cities'
qualified=run('san francisco',fav='San Francisco|America/Los_Angeles')[0]
assert qualified['mods']['alt']['arg']==''
assert run('berlin',fav='Berlin\nberlin')[0]['mods']['alt']['arg']==''
assert run('tokyo',fav='Atlantis')[0]['mods']['alt']['arg']=='Atlantis\nTokyo|Asia/Tokyo'
d=plistlib.loads((root/'workflow/info.plist').read_bytes())
f=next(o for o in d['objects'] if o['type']=='alfred.workflow.input.scriptfilter')
connections=d['connections'][f['uid']]
alt=next(c for c in connections if c['modifiers']==524288)
action=next(o for o in d['objects'] if o['uid']==alt['destinationuid'])
assert action['type']=='alfred.workflow.action.script'
assert action['version']==2, 'Alfred Run Script actions require object version 2'
assert 'toggle-favourite.js "$1"' in action['config']['script']
assert next(c for c in connections if c['modifiers']==0)['destinationuid']!=alt['destinationuid']
print('Favourite modifier payload, add/remove round trip, unmarked city names, last removal, qualification, duplicate removal, and Alfred routing passed.')
