#!/usr/bin/env python3
"""Deterministic conversion, day crossing, DST, and modifier-routing checks."""
import datetime,json,os,pathlib,shutil,subprocess,zoneinfo
root=pathlib.Path(__file__).resolve().parents[1];build=root/'.build'
source=(root/'workflow/main.swift').read_text().replace('let now = Date()','let now = Date(timeIntervalSince1970: Double(ProcessInfo.processInfo.environment["TEST_EPOCH"]!)!)')
(build/'test-conversion.swift').write_text(source)
subprocess.run(['xcrun','swiftc','-O','-module-cache-path',str(build/'module-cache'),str(build/'test-conversion.swift'),'-o',str(build/'test-conversion')],check=True)
shutil.copy2(root/'workflow/cities.json',build/'cities.json')
def run(q,instant='2026-10-25T12:00:00+00:00',local='Europe/Dublin',fmt='1'):
    env=dict(os.environ,TZ=local,TEST_EPOCH=str(datetime.datetime.fromisoformat(instant).timestamp()),use_24_hour=fmt)
    return json.loads(subprocess.check_output([str(build/'test-conversion'),q],env=env))['items'][0]
for query in ['berlin 3pm','berlin 3:00pm','berlin 3:00 pm','berlin 15:00','berlin 15']:
    r=run(query);assert r['arg']=='14:00',r
    assert r['mods']['alt']['arg']==query+' @local'
    assert r['mods']['alt']['variables']['clock_action']=='convert'
    assert r['variables']['clock_action']=='copy'
r=run('berlin 3pm @local');assert r['arg']=='16:00',r
assert r['mods']['alt']['arg']=='berlin 3pm'
assert run('berlin 12am')['arg']=='23:00'
assert 'Sat 24 Oct' in run('berlin 12am')['subtitle']
assert run('berlin 12pm')['arg']=='11:00'
assert run('tokyo 11:30pm @local')['arg']=='08:30'
assert 'Mon 26 Oct' in run('tokyo 11:30pm @local')['subtitle']
assert run('kathmandu 3pm')['arg']=='09:15'
assert run('berlin 3pm',fmt='0')['arg']=='2:00 PM'
for q in ['berlin 25:00','berlin 13pm','berlin 0am','berlin 3:99pm']:
    assert run(q)['title']=='Invalid time'
r=run('berlin 2:30am',instant='2026-03-29T12:00:00+00:00');assert r['valid']==False,r
r=run('berlin 2:30am');assert r['arg']=='01:30' and 'First occurrence' in r['subtitle'],r
r=run('berlin 3pm',instant='2026-07-01T12:00:00+00:00');assert r['arg']=='14:00'
r=run('berlin');assert r['mods']['alt']['variables']['clock_action']=='favourite'
assert '→' not in r['title']
print('Conversion formats, directions, clipboard arguments, dates, fractional offsets, invalid times, DST gaps/repeats, and favourite routing passed.')
