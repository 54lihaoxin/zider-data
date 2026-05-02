from __future__ import annotations

import json
from pathlib import Path

from ziderdata.schema import GraphicsEntry


def parse(path: Path) -> list[GraphicsEntry]:
    entries = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(GraphicsEntry(
                character=data['character'],
                strokes=data.get('strokes', []),
                medians=data.get('medians', []),
            ))
    return entries
