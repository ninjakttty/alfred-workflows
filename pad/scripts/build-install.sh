#!/bin/zsh
set -eu
cd "${0:A:h}/.."
# Optional first argument: installed Alfred workflow directory (for synced preferences).
target="${1:-}"
if /usr/bin/pgrep -x Scratchpad >/dev/null; then
  print -u2 'Quit Scratchpad before rebuilding, then rerun this script.'; exit 1
fi
swift test
swift build -c release
app="$PWD/workflow/.scratchpad/Scratchpad.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
cp "$(swift build -c release --show-bin-path)/Scratchpad" "$app/Contents/MacOS/Scratchpad"
cp resources/Info.plist "$app/Contents/Info.plist"
cp workflow/icon.png "$app/Contents/Resources/icon.png"
cp scripts/scratchpad workflow/scratchpad
chmod +x workflow/scratchpad
/usr/bin/codesign --force --sign - "$app"
python3 - <<'PY'
from pathlib import Path
import zipfile
with zipfile.ZipFile('pad.alfredworkflow', 'w', zipfile.ZIP_DEFLATED) as z:
    for file in sorted(Path('workflow').rglob('*')):
        if file.is_file(): z.write(file, file.relative_to('workflow'))
PY
if [[ -z "$target" ]]; then
  target="$(python3 - <<'PY'
import os, pathlib, plistlib
root = pathlib.Path.home() / 'Library/Application Support/Alfred/Alfred.alfredpreferences/workflows'
for path in root.glob('*/info.plist'):
    try:
        if plistlib.load(path.open('rb')).get('bundleid') in ('net.ninjakitty.pad', 'net.ninjakitty.scratchpad'):
            print(path.parent); break
    except (OSError, ValueError): pass
PY
)"
fi
if [[ -n "$target" ]]; then
  [[ -f "$target/info.plist" ]] || { print -u2 'Target must be an existing Alfred workflow directory.'; exit 1; }
  /usr/bin/ditto workflow "$target"
  mkdir -p "$HOME/.local/bin"
  # Remove a legacy symlink before copying, rather than following its old target.
  if [[ -L "$HOME/.local/bin/scratchpad" ]]; then unlink "$HOME/.local/bin/scratchpad"; fi
  cp scripts/scratchpad-cli "$HOME/.local/bin/scratchpad"
  chmod +x "$HOME/.local/bin/scratchpad"
  print "Updated bundled workflow in $target"
else
  print 'Built pad.alfredworkflow. Open it to import into Alfred.'
fi
