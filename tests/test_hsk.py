import json
import tempfile
import unittest
from pathlib import Path

from ziderdata.hsk import parse


class TestParseHsk(unittest.TestCase):
    def _write(self, tmp_dir: str, entries: list[dict]) -> Path:
        path = Path(tmp_dir) / 'complete.json'
        path.write_text(json.dumps(entries, ensure_ascii=False), encoding='utf-8')
        return path

    def test_full_entry(self):
        data = [{
            'simplified': '爱好',
            'frequency': 4902,
            'level': ['newest-2', 'new-1', 'old-3'],
            'pos': ['n', 'v'],
            'forms': [{
                'transcriptions': {'pinyin': 'ài hào'},
                'meanings': ['to like; to be fond of', 'interest; hobby'],
                'classifiers': ['个'],
            }],
        }]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e.simplified, '爱好')
        self.assertEqual(e.frequency, 4902)
        self.assertEqual(e.pos, ['n', 'v'])
        self.assertEqual(e.hsk_new, 1)
        self.assertEqual(e.hsk_newest, 2)
        self.assertEqual(e.hsk_old, 3)
        self.assertEqual(len(e.forms), 1)
        f = e.forms[0]
        self.assertEqual(f.pinyin, 'ài hào')
        self.assertEqual(f.meanings, ['to like; to be fond of', 'interest; hobby'])
        self.assertEqual(f.classifiers, ['个'])

    def test_multiple_forms(self):
        data = [{
            'simplified': '啊',
            'frequency': 47,
            'level': ['new-2'],
            'forms': [
                {'transcriptions': {'pinyin': 'ā'}, 'meanings': ['interjection of surprise'], 'classifiers': []},
                {'transcriptions': {'pinyin': 'á'}, 'meanings': ['interjection expressing doubt'], 'classifiers': []},
            ],
        }]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        e = entries[0]
        self.assertEqual(len(e.forms), 2)
        self.assertEqual(e.forms[0].pinyin, 'ā')
        self.assertEqual(e.forms[1].pinyin, 'á')

    def test_partial_levels(self):
        data = [{'simplified': '测', 'level': ['new-4'], 'forms': []}]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        e = entries[0]
        self.assertEqual(e.hsk_new, 4)
        self.assertIsNone(e.hsk_newest)
        self.assertIsNone(e.hsk_old)

    def test_missing_optional_fields(self):
        data = [{'simplified': '测', 'forms': [{'transcriptions': {}, 'meanings': [], 'classifiers': []}]}]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        e = entries[0]
        self.assertIsNone(e.frequency)
        self.assertIsNone(e.hsk_new)
        self.assertIsNone(e.forms[0].pinyin)

    def test_multiple_entries(self):
        data = [
            {'simplified': '爱', 'level': ['new-1'], 'forms': []},
            {'simplified': '爱好', 'level': ['new-1'], 'forms': []},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].simplified, '爱')
        self.assertEqual(entries[1].simplified, '爱好')

    def test_empty_classifiers_preserved(self):
        data = [{'simplified': '爱', 'level': ['new-1'], 'forms': [
            {'transcriptions': {'pinyin': 'ài'}, 'meanings': ['to love'], 'classifiers': []},
        ]}]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, data))
        self.assertEqual(entries[0].forms[0].classifiers, [])


if __name__ == '__main__':
    unittest.main()
