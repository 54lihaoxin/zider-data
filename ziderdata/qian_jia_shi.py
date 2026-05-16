from __future__ import annotations

import json
import re
from pathlib import Path

from opencc import OpenCC

from ziderdata.schema import ArticleEntry

_t2s = OpenCC('t2s')

_PUNCT_RE = re.compile(r'[^㐀-鿿豈-﫿\s]')
_ANNOTATION_RE = re.compile(r'[（(][^）)]*[）)]')
# Dynasty prefix e.g. （唐）, （宋）
_DYNASTY_RE = re.compile(r'^[（(][^）)]+[）)]\s*')


def _sanitize(text: str) -> str:
    text = _ANNOTATION_RE.sub(' ', text)
    text = _PUNCT_RE.sub(' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def parse(path: Path) -> list[ArticleEntry]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    entries = []
    for section in data['content']:
        for poem in section['content']:
            title = _t2s.convert(poem['chapter'])
            author = _t2s.convert(_DYNASTY_RE.sub('', poem['author']))
            paragraphs = [p for p in poem['paragraphs'] if isinstance(p, str)]
            text = _sanitize(_t2s.convert(' '.join(paragraphs)))
            entries.append(ArticleEntry(title=title, author=author, text=text))
    return entries
