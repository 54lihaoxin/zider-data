import json
import tempfile
import unittest
from pathlib import Path

from ziderdata.makemeahanzi_dictionary import parse


class TestParseDictionary(unittest.TestCase):
    def _write(self, tmp_dir: str, lines: list[str]) -> Path:
        path = Path(tmp_dir) / 'dictionary.txt'
        path.write_text('\n'.join(lines), encoding='utf-8')
        return path

    def test_full_entry(self):
        line = json.dumps({
            'character': '好',
            'pinyin': ['hǎo', 'hào'],
            'definition': 'good, well',
            'decomposition': '⿰女子',
            'radical': '女',
            'etymology': {'type': 'ideographic', 'hint': 'A woman with a child'},
            'matches': [[0], [1]],
        })
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, [line]))
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e.character, '好')
        self.assertEqual(e.pinyin, ['hǎo', 'hào'])
        self.assertEqual(e.definition, 'good, well')
        self.assertEqual(e.decomposition, '⿰女子')
        self.assertEqual(e.radical, '女')
        self.assertIsNotNone(e.etymology)
        self.assertEqual(e.etymology['type'], 'ideographic')

    def test_minimal_entry(self):
        line = json.dumps({
            'character': '⺀',
            'pinyin': [],
            'decomposition': '？',
            'radical': '⺀',
            'matches': [None, None],
        })
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, [line]))
        e = entries[0]
        self.assertIsNone(e.definition)
        self.assertIsNone(e.etymology)
        self.assertEqual(e.pinyin, [])

    def test_multiple_entries(self):
        lines = [
            json.dumps({'character': '一', 'pinyin': ['yī'], 'definition': 'one', 'decomposition': '？', 'radical': '一', 'matches': [None]}),
            json.dumps({'character': '二', 'pinyin': ['èr'], 'definition': 'two', 'decomposition': '？', 'radical': '二', 'matches': [None]}),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, lines))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].character, '一')
        self.assertEqual(entries[1].character, '二')

    def test_blank_lines_ignored(self):
        line = json.dumps({'character': '一', 'pinyin': ['yī'], 'decomposition': '？', 'radical': '一', 'matches': [None]})
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, ['', line, '']))
        self.assertEqual(len(entries), 1)


if __name__ == '__main__':
    unittest.main()
