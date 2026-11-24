#!/usr/bin/env python3
from pathlib import Path
import plistlib
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(root / 'tests'), '-v'], check=True)
workflow = root / 'workflow'
info = plistlib.loads((workflow / 'info.plist').read_bytes())
info['readme'] = (root / 'README.md').read_text()
(workflow / 'info.plist').write_bytes(plistlib.dumps(info))
with zipfile.ZipFile(root / 'weather.alfredworkflow', 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(workflow.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts:
            archive.write(file, file.relative_to(workflow))
print('Built weather/weather.alfredworkflow')
