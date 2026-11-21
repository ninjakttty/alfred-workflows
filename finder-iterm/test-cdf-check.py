import contextlib
import io
import plistlib
import runpy
import subprocess
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parent


class CdfCheckTests(unittest.TestCase):
    def test_iterm_states(self):
        for running, windows, expected in [
            ('true', '1', 'cdf'),
            ('false', None, 'cdi'),
            ('true', '0', 'cdi'),
        ]:
            with self.subTest(running=running, windows=windows):
                results = [subprocess.CompletedProcess([], 0, running, '')]
                if windows is not None:
                    results.append(subprocess.CompletedProcess([], 0, windows, ''))
                output = io.StringIO()
                with patch('subprocess.run', side_effect=results), contextlib.redirect_stdout(output):
                    runpy.run_path(str(ROOT / 'cdf-check.py'), run_name='__main__')
                self.assertEqual(ET.fromstring(output.getvalue()).find('item').get('arg'), expected)

    def test_keyword_accepts_no_argument(self):
        info = plistlib.loads((ROOT / 'info.plist').read_bytes())
        keyword = next(obj for obj in info['objects'] if obj['uid'] == 'cdf-keyword')
        self.assertEqual(keyword['config']['argumenttype'], 2)

    def test_export_matches_source(self):
        with zipfile.ZipFile(ROOT / 'finder-iterm.alfredworkflow') as archive:
            self.assertIsNone(archive.testzip())
            for name in ['info.plist', 'cdf-check.py', 'cdf.applescript', 'cdi.applescript', 'icon.png']:
                self.assertEqual(archive.read(name), (ROOT / name).read_bytes(), name)


if __name__ == '__main__':
    unittest.main()
