#!/usr/bin/env python3
"""Alfred UI persistence and visibility bridge. No third-party dependencies."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

DATA = Path(os.environ.get('alfred_workflow_data') or Path.home() / 'Library/Application Support/Alfred/Workflow Data/net.ninjakitty.pad')
CACHE = Path(os.environ.get('alfred_workflow_cache') or Path.home() / 'Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/net.ninjakitty.pad')
NOTE = DATA / 'note.txt'
SESSION = CACHE / 'alfredui-session.json'
CLOSE = CACHE / 'alfredui-close'


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_note():
    try:
        return NOTE.read_text(encoding='utf-8')
    except FileNotFoundError:
        pass
    return ''


def live_session():
    try:
        data = json.loads(SESSION.read_text())
    except FileNotFoundError:
        return False
    result = subprocess.run(['/bin/ps', '-p', str(data['pid']), '-o', 'comm='], capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip().endswith('/Alfred UI')


def ui_pid():
    pid = os.getppid()
    for _ in range(8):
        result = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'ppid=', '-o', 'comm='], capture_output=True, text=True, check=True)
        parent, command = result.stdout.strip().split(None, 1)
        if command.endswith('/Alfred UI'):
            return pid
        pid = int(parent)
    raise RuntimeError('Cannot identify the Alfred UI host process')


def update(**ids):
    return {'update': {'ids': ids}}


def main(command, text='', loaded='true'):
    if command == 'load':
        # An unreadable note never becomes a writable blank editor.
        text = load_note()
        CLOSE.unlink(missing_ok=True)
        atomic_write(SESSION, json.dumps({'pid': ui_pid()}))
        return {**update(editor={'text': text, 'editable': True}, status={'text': '', 'hidden': True}), 'variables': {'loaded': True}}
    if command == 'close' and loaded.lower() not in ('true', '1'):
        return {'functions': {'ids': {'pad-window': 'close'}}}
    if command in ('save', 'close'):
        atomic_write(NOTE, text)
        if command == 'close':
            SESSION.unlink(missing_ok=True)
            CLOSE.unlink(missing_ok=True)
            return {'functions': {'ids': {'pad-window': 'close'}}}
        return {**update(status={'text': '', 'hidden': True}), 'pulse': {'interval': 0.25}}
    if command == 'poll':
        if CLOSE.exists():
            # Edits save synchronously; a failed save disables this pulse.
            SESSION.unlink(missing_ok=True)
            CLOSE.unlink(missing_ok=True)
            return {'functions': {'ids': {'pad-window': 'close'}}}
        return {}
    if command in ('toggle', 'show', 'hide', 'quit'):
        running = live_session()
        if command in ('hide', 'quit') or (command == 'toggle' and running):
            if running:
                atomic_write(CLOSE, '')
            return None
        subprocess.run(['/usr/bin/osascript', '-e', 'tell application id "com.runningwithcrayons.Alfred" to run trigger "ui-launch" in workflow "net.ninjakitty.pad"'], check=True)
        return None
    raise ValueError('Unknown command: ' + command)


if __name__ == '__main__':
    try:
        result = main(*sys.argv[1:])
    except Exception as error:
        print('Pad: ' + str(error), file=sys.stderr)
        result = {**update(status={'text': 'Could not save/load: ' + str(error), 'colour': 'systemRedColor', 'hidden': False}), 'pulse': {'interval': 0}}
        print(json.dumps(result))
        # Alfred UI only processes action JSON from successful script exits.
        # Keep CLI failures nonzero; UI failures are represented by the error label.
        sys.exit(1 if sys.argv[1] in ('toggle', 'show', 'hide', 'quit') else 0)
    if result is not None:
        print(json.dumps(result, ensure_ascii=False))
