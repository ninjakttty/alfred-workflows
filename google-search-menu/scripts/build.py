import json
from pathlib import Path
import plistlib
import zipfile

root = Path(__file__).resolve().parents[1]
images = root / 'List Filter Images'
images.mkdir(exist_ok=True)
info = plistlib.loads((root / 'info.plist').read_bytes())
menu = next(node for node in info['objects'] if node['type'].endswith('listfilter'))
items = json.loads(menu['config']['items'])
info['readme'] = (root / 'README.md').read_text()
(root / 'info.plist').write_bytes(plistlib.dumps(info))
with zipfile.ZipFile(root / 'google-search-menu.alfredworkflow', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in ['info.plist', 'open-chrome.applescript', 'icon.png', 'README.md']:
        archive.write(root / name, name)
    for item in items:
        path = images / item['imagefile']
        archive.write(path, str(path.relative_to(root)))
