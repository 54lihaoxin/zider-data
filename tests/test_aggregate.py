import unittest
from io import StringIO
from unittest.mock import patch

from ziderdata.aggregate import validate
from ziderdata.schema import DictionaryEntry, GraphicsEntry


def _dict_entry(char: str) -> DictionaryEntry:
    return DictionaryEntry(character=char, pinyin=['pīn'], definition='test')


def _graphics_entry(char: str) -> GraphicsEntry:
    return GraphicsEntry(character=char, strokes=['M 1 1 Z'], medians=[[[1, 1]]])


class TestValidate(unittest.TestCase):
    def test_common_characters_included(self):
        dictionary = {c: _dict_entry(c) for c in ['一', '二', '三']}
        graphics = {c: _graphics_entry(c) for c in ['一', '二', '三']}
        result = validate(dictionary, graphics)
        self.assertEqual(result, sorted(['一', '二', '三']))

    def test_dictionary_only_dropped(self):
        dictionary = {c: _dict_entry(c) for c in ['一', '二']}
        graphics = {'一': _graphics_entry('一')}
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            result = validate(dictionary, graphics)
        self.assertNotIn('二', result)
        self.assertIn('二', mock_out.getvalue())
        self.assertIn('[DROP]', mock_out.getvalue())

    def test_graphics_only_dropped(self):
        dictionary = {'一': _dict_entry('一')}
        graphics = {c: _graphics_entry(c) for c in ['一', '二']}
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            result = validate(dictionary, graphics)
        self.assertNotIn('二', result)
        self.assertIn('二', mock_out.getvalue())
        self.assertIn('[DROP]', mock_out.getvalue())

    def test_empty_inputs(self):
        result = validate({}, {})
        self.assertEqual(result, [])

    def test_no_overlap_all_dropped(self):
        dictionary = {'一': _dict_entry('一')}
        graphics = {'二': _graphics_entry('二')}
        with patch('sys.stdout', new_callable=StringIO):
            result = validate(dictionary, graphics)
        self.assertEqual(result, [])

    def test_result_is_sorted(self):
        dictionary = {c: _dict_entry(c) for c in ['三', '一', '二']}
        graphics = {c: _graphics_entry(c) for c in ['三', '一', '二']}
        result = validate(dictionary, graphics)
        self.assertEqual(result, sorted(result))


if __name__ == '__main__':
    unittest.main()
