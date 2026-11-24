import importlib.util
from pathlib import Path
import tempfile
import subprocess
import os
import json
import unittest

spec = importlib.util.spec_from_file_location('note', Path(__file__).parents[1] / 'workflow/pad.alfredui/scripts/note.py')
note = importlib.util.module_from_spec(spec)
spec.loader.exec_module(note)


class PersistenceTests(unittest.TestCase):
    def test_atomic_unicode_empty_and_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'nested/note.txt'
            for text in ['hello\n世界 🐱', 'replacement', '']:
                note.atomic_write(path, text)
                self.assertEqual(path.read_text(), text)
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_failed_write_preserves_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'note.txt'
            path.write_text('original')
            with self.assertRaises(OSError):
                note.atomic_write(path / 'child', 'replacement')
            self.assertEqual(path.read_text(), 'original')

    def test_invalid_utf8_is_not_blank(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = note.NOTE
            try:
                note.NOTE = Path(directory) / 'note.txt'
                note.NOTE.write_bytes(b'\xff')
                with self.assertRaises(UnicodeError):
                    note.main('load')
                self.assertEqual(note.NOTE.read_bytes(), b'\xff')
            finally:
                note.NOTE = previous

    def test_read_only_close_does_not_overwrite_note(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = note.NOTE
            try:
                note.NOTE = Path(directory) / 'note.txt'
                note.NOTE.write_bytes(b'\xff')
                result = note.main('close', '', 'false')
                self.assertEqual(result['functions']['ids']['pad-window'], 'close')
                self.assertEqual(note.NOTE.read_bytes(), b'\xff')
            finally:
                note.NOTE = previous

    def test_successful_save_clears_error_without_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = note.NOTE
            try:
                note.NOTE = Path(directory) / 'note.txt'
                status = note.main('save', 'note')['update']['ids']['status']
                self.assertEqual(status, {'text': '', 'hidden': True})
                self.assertEqual(note.NOTE.read_text(), 'note')
            finally:
                note.NOTE = previous

    def test_failed_close_preserves_open_session_and_note(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = note.NOTE, note.SESSION, note.CLOSE
            try:
                original = Path(directory) / 'note.txt'
                original.write_text('original')
                note.NOTE = original / 'invalid-child'
                note.SESSION = Path(directory) / 'session.json'
                note.CLOSE = Path(directory) / 'close'
                note.SESSION.write_text('active session')
                note.CLOSE.touch()
                with self.assertRaises(OSError):
                    note.main('close', 'unsaved edit')
                self.assertEqual(original.read_text(), 'original')
                self.assertEqual(note.SESSION.read_text(), 'active session')
                self.assertTrue(note.CLOSE.exists())
            finally:
                note.NOTE, note.SESSION, note.CLOSE = previous

    def test_ui_save_failure_returns_displayable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            (data / 'note.txt').mkdir()
            result = subprocess.run(
                [os.sys.executable, str(Path(note.__file__)), 'close', 'unsaved edit'],
                env={**os.environ, 'alfred_workflow_data': directory},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            action = json.loads(result.stdout)
            self.assertFalse(action['update']['ids']['status']['hidden'])
            self.assertNotIn('functions', action)
            self.assertIn('Pad:', result.stderr)
