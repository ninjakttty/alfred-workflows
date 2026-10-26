#!/usr/bin/env python3
"""Exercise production formatting at fixed instants around 2026 DST changes."""
import datetime,json,os,pathlib,subprocess,zoneinfo,shutil
root=pathlib.Path(__file__).resolve().parents[1]
build=root/'.build';build.mkdir(exist_ok=True)
source=(root/'workflow/main.swift').read_text()
needle='let now = Date()'
assert needle in source
(build/'test-dst.swift').write_text(source.replace(needle,'let now = Date(timeIntervalSince1970: Double(ProcessInfo.processInfo.environment["TEST_EPOCH"]!)!)'))
subprocess.run(['xcrun','swiftc','-O','-module-cache-path',str(build/'module-cache'),str(build/'test-dst.swift'),'-o',str(build/'test-dst')],check=True)
shutil.copy2(root/'workflow/cities.json',build/'cities.json')
for iso in ['2026-03-08T09:59:00+00:00','2026-03-08T10:01:00+00:00','2026-03-29T00:59:00+00:00','2026-03-29T01:01:00+00:00','2026-10-25T00:59:00+00:00','2026-10-25T01:01:00+00:00','2026-11-01T08:59:00+00:00','2026-11-01T09:01:00+00:00']:
    dt=datetime.datetime.fromisoformat(iso)
    result=json.loads(subprocess.check_output([str(build/'test-dst')],env=dict(os.environ,TEST_EPOCH=str(dt.timestamp()),TZ='Europe/Dublin')))
    for item,z in zip(result['items'],['America/Los_Angeles','Europe/Dublin','Europe/Berlin']):
        expected=dt.astimezone(zoneinfo.ZoneInfo(z)).strftime('%I:%M %p').lstrip('0')
        assert item['arg']==expected,(iso,item,expected)
print('24 daylight saving boundary checks passed.')
