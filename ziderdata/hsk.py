from __future__ import annotations

import json
from pathlib import Path

from ziderdata.schema import HskEntry, HskForm


def parse(path: Path) -> list[HskEntry]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    entries = []
    for item in data:
        levels: dict[str, int] = {}
        for lv in item.get('level', []):
            curriculum, num = lv.rsplit('-', 1)
            levels[curriculum] = int(num)
        forms = []
        for form in item.get('forms', []):
            trans = form.get('transcriptions', {})
            forms.append(HskForm(
                pinyin=trans.get('pinyin'),
                meanings=form.get('meanings', []),
                classifiers=form.get('classifiers', []),
            ))
        entries.append(HskEntry(
            simplified=item['simplified'],
            frequency=item.get('frequency'),
            pos=item.get('pos', []),
            hsk_new=levels.get('new'),
            hsk_newest=levels.get('newest'),
            hsk_old=levels.get('old'),
            forms=forms,
        ))
    return entries
