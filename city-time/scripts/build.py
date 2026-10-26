#!/usr/bin/env python3
"""Build the native executable and package the Alfred workflow on macOS."""
import base64
import pathlib
import plistlib
import shutil
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflow"
BUILD = ROOT / ".build"
BUILD.mkdir(exist_ok=True)
subprocess.run(["xcrun", "swiftc", "-O", "-module-cache-path", str(BUILD / "module-cache"), str(WORKFLOW / "main.swift"), "-o", str(BUILD / "city-time")], check=True)
shutil.copy2(WORKFLOW / "cities.json", BUILD / "cities.json")
(WORKFLOW / "city-time.b64").write_text(base64.b64encode((BUILD / "city-time").read_bytes()).decode())
metadata = plistlib.loads((WORKFLOW / "info.plist").read_bytes())
for obj in metadata["objects"]:
    if obj["type"] == "alfred.workflow.input.scriptfilter":
        obj["config"]["script"] = (WORKFLOW / "run.zsh").read_text()
(WORKFLOW / "info.plist").write_bytes(plistlib.dumps(metadata))
output = ROOT / "dist" / "city-time.alfredworkflow"
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(WORKFLOW.iterdir()):
        if file.is_file():
            archive.write(file, file.name)
print(output)
