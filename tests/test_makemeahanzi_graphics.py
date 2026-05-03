import json
import tempfile
import unittest
from pathlib import Path

from ziderdata.makemeahanzi_graphics import parse


class TestParseGraphics(unittest.TestCase):
    def _write(self, tmp_dir: str, lines: list[str]) -> Path:
        path = Path(tmp_dir) / 'graphics.txt'
        path.write_text('\n'.join(lines), encoding='utf-8')
        return path

    def test_full_entry(self):
        line = json.dumps({
            'character': '好',
            'strokes': ['M 441 666 Q 490 726 523 749 Z', 'M 527 467 L 604 554 Z'],
            'medians': [[[441, 666], [490, 726], [523, 749]], [[527, 467], [604, 554]]],
        })
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, [line]))
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e.character, '好')
        self.assertEqual(len(e.strokes), 2)
        self.assertEqual(len(e.medians), 2)
        self.assertEqual(e.medians[0][0], [441, 666])

    def test_stroke_count_matches_median_count(self):
        line = json.dumps({
            'character': '三',
            'strokes': ['M 1 1 Z', 'M 2 2 Z', 'M 3 3 Z'],
            'medians': [[[1, 1]], [[2, 2]], [[3, 3]]],
        })
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, [line]))
        e = entries[0]
        self.assertEqual(len(e.strokes), len(e.medians))

    def test_multiple_entries(self):
        lines = [
            json.dumps({'character': '一', 'strokes': ['M 1 1 Z'], 'medians': [[[1, 1]]]}),
            json.dumps({'character': '二', 'strokes': ['M 2 2 Z', 'M 3 3 Z'], 'medians': [[[2, 2]], [[3, 3]]]}),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, lines))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1].character, '二')

    def test_blank_lines_ignored(self):
        line = json.dumps({'character': '一', 'strokes': ['M 1 1 Z'], 'medians': [[[1, 1]]]})
        with tempfile.TemporaryDirectory() as tmp:
            entries = parse(self._write(tmp, ['', line, '']))
        self.assertEqual(len(entries), 1)


if __name__ == '__main__':
    unittest.main()
