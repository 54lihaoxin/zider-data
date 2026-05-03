from __future__ import annotations

import json
from pathlib import Path

from ziderdata.schema import MmahDictionaryEntry


def parse(path: Path) -> list[MmahDictionaryEntry]:
    entries = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(MmahDictionaryEntry(
                character=data['character'],
                pinyin=data.get('pinyin', []),
                definition=data.get('definition'),
                decomposition=data.get('decomposition'),
                radical=data.get('radical'),
                etymology=data.get('etymology'),
                matches=data.get('matches', []),
            ))
    return entries
