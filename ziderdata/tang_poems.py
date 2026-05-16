from __future__ import annotations

import json
import re
from pathlib import Path

from opencc import OpenCC

from ziderdata.schema import ArticleEntry

_t2s = OpenCC('t2s')

# Keep only CJK ideographs and whitespace; collapse runs of whitespace
_PUNCT_RE = re.compile(r'[^㐀-鿿豈-﫿\s]')
# Strip parenthetical annotations before sanitizing, e.g. (顰 一作：蹙)
_ANNOTATION_RE = re.compile(r'[（(][^）)]*[）)]')


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
            author = _t2s.convert(poem['author'])
            poem_text = _sanitize(_t2s.convert(' '.join(poem['paragraphs'])))
            entries.append(ArticleEntry(title=title, author=author, text=poem_text))
    return entries
