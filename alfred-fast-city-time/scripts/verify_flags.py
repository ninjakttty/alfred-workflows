#!/usr/bin/env python3
"""Verify bundled country codes and visible flags without altering user data."""
import json,os,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
def run(q):
    return json.loads(subprocess.check_output([str(root/'.build/city-time'),q],env=dict(os.environ,favourite_cities='San Francisco\nDublin\nBerlin')))['items'][0]
for city,flag,country in [('San Francisco','🇺🇸','United States'),('Dublin','🇮🇪','Ireland'),('Berlin','🇩🇪','Germany'),('Tokyo','🇯🇵','Japan'),('Kathmandu','🇳🇵','Nepal'),('Manchester','🇬🇧','United Kingdom')]:
    item=run(city)
    assert item['subtitle'].startswith(flag+' '+country+' · '),item
    assert flag not in item['title'] and flag not in item['arg']
assert run('UTC')['subtitle'].startswith('🌐 Universal · ')
assert run('berlin 3pm')['subtitle'].startswith('🇩🇪 Germany · ')
assert run('berlin 3pm @local')['subtitle'].startswith('🇩🇪 Germany · ')
rows=json.loads((root/'workflow/cities.json').read_text())
assert len(rows)==431
assert all(r.get('countryCode') and len(r['countryCode'])==2 and r['countryCode'].isascii() and r['countryCode'].isalpha() for r in rows if r['city']!='UTC')
print('Country flags, additional cities, UTC fallback, conversion subtitles, unchanged copy text, and all 431 bundled country mappings passed.')
