#!/bin/zsh
set -eu
cd "${0:A:h}/.."
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 - <<'PY'
from pathlib import Path
import zipfile
with zipfile.ZipFile('pad.alfredworkflow', 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(Path('workflow').rglob('*')):
        if file.is_file() and '.scratchpad' not in file.parts and '__pycache__' not in file.parts:
            archive.write(file, file.relative_to('workflow'))
PY
if [[ -n "${1:-}" ]]; then
  [[ -f "$1/info.plist" ]] || { print -u2 'Target must be an existing Alfred workflow directory.'; exit 1; }
  /usr/bin/ditto workflow/pad.alfredui "$1/pad.alfredui"
  cp workflow/info.plist workflow/icon.png workflow/scratchpad "$1/"
  print "Updated Pad in $1"
else
  print 'Built pad.alfredworkflow. Open it to import into Alfred.'
fi
