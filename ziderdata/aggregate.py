from __future__ import annotations

import sqlite3
from pathlib import Path

from opencc import OpenCC
from ziderdata.encoding import encode_median, encode_path
from ziderdata.schema import MmahDictionaryEntry, MmahGraphicsEntry, HskEntry

_s2t = OpenCC('s2t')

CREATE_SCHEMA = '''
    CREATE TABLE mmah_characters (
        id                INTEGER PRIMARY KEY,
        character         TEXT    NOT NULL UNIQUE,
        pinyin            TEXT,
        decomposition     TEXT,
        radical           TEXT,
        stroke_count      INTEGER,
        etymology_type_id INTEGER REFERENCES mmah_etymology_types(id)
    );

    CREATE TABLE mmah_etymology_types (
        id      INTEGER PRIMARY KEY,
        name    TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE mmah_strokes (
        character_id    INTEGER NOT NULL REFERENCES mmah_characters(id),
        stroke_index    INTEGER NOT NULL,
        path            BLOB    NOT NULL,
        median          BLOB    NOT NULL,
        PRIMARY KEY (character_id, stroke_index)
    ) WITHOUT ROWID;

    CREATE TABLE hsk_words (
        id          INTEGER PRIMARY KEY,
        simplified  TEXT    NOT NULL UNIQUE,
        traditional TEXT    NOT NULL,
        frequency   INTEGER,
        pos         TEXT,
        hsk_old     INTEGER,
        hsk_new     INTEGER,
        hsk_newest  INTEGER
    );

    CREATE TABLE hsk_word_forms (
        word_id     INTEGER NOT NULL REFERENCES hsk_words(id),
        form_index  INTEGER NOT NULL,
        pinyin      TEXT,
        classifiers TEXT,
        meanings    TEXT,
        PRIMARY KEY (word_id, form_index)
    ) WITHOUT ROWID;
'''


def validate(dictionary: dict[str, MmahDictionaryEntry], graphics: dict[str, MmahGraphicsEntry]) -> list[str]:
    dict_chars = set(dictionary)
    graphics_chars = set(graphics)

    for char in sorted(dict_chars - graphics_chars):
        print(f'[DROP] {char!r}: in dictionary.txt only — skipped')
    for char in sorted(graphics_chars - dict_chars):
        print(f'[DROP] {char!r}: in graphics.txt only — skipped')

    return sorted(dict_chars & graphics_chars)


def _collect_etymology_types(characters: list[str], dictionary: dict[str, MmahDictionaryEntry]) -> dict[str, int]:
    types: dict[str, int] = {}
    for char in characters:
        ety = dictionary[char].etymology
        if ety and (t := ety.get('type')) and t not in types:
            types[t] = len(types)
    return types


def build_database(
    characters: list[str],
    dictionary: dict[str, MmahDictionaryEntry],
    graphics: dict[str, MmahGraphicsEntry],
    hsk_entries: list[HskEntry],
    output_dir: Path,
) -> None:
    db_path = output_dir / 'zider-data.sqlite'
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.executescript(CREATE_SCHEMA)

    etymology_type_ids = _collect_etymology_types(characters, dictionary)
    for name, eid in etymology_type_ids.items():
        conn.execute('INSERT INTO mmah_etymology_types (id, name) VALUES (?, ?)', (eid, name))

    for char in characters:
        d = dictionary[char]
        g = graphics[char]
        ety = d.etymology or {}

        ety_type = ety.get('type')
        cursor = conn.execute(
            'INSERT INTO mmah_characters (character, pinyin, decomposition, radical, stroke_count, etymology_type_id) VALUES (?, ?, ?, ?, ?, ?)',
            (
                d.character,
                ' '.join(d.pinyin) if d.pinyin else None,
                d.decomposition,
                d.radical,
                len(g.strokes),
                etymology_type_ids[ety_type] if ety_type else None,
            ),
        )
        character_id = cursor.lastrowid

        for i, (path, median) in enumerate(zip(g.strokes, g.medians)):
            conn.execute(
                'INSERT INTO mmah_strokes (character_id, stroke_index, path, median) VALUES (?, ?, ?, ?)',
                (character_id, i, encode_path(path), encode_median(median)),
            )

    for entry in hsk_entries:
        cursor = conn.execute(
            'INSERT INTO hsk_words (simplified, traditional, frequency, pos, hsk_old, hsk_new, hsk_newest) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (entry.simplified, _s2t.convert(entry.simplified), entry.frequency, '|'.join(entry.pos) if entry.pos else None, entry.hsk_old, entry.hsk_new, entry.hsk_newest),
        )
        word_id = cursor.lastrowid

        for i, form in enumerate(entry.forms):
            conn.execute(
                'INSERT INTO hsk_word_forms (word_id, form_index, pinyin, classifiers, meanings) VALUES (?, ?, ?, ?, ?)',
                (
                    word_id,
                    i,
                    form.pinyin,
                    '|'.join(form.classifiers) if form.classifiers else None,
                    '|'.join(form.meanings) if form.meanings else None,
                ),
            )

    conn.commit()
    conn.execute('VACUUM')
    conn.close()
    print(f'Wrote {len(characters)} characters and {len(hsk_entries)} words to {db_path}')


def run(
    hsk_entries: list[HskEntry],
    mmah_dictionary_entries: list[MmahDictionaryEntry],
    mmah_graphics_entries: list[MmahGraphicsEntry],
    output_dir: Path,
) -> None:
    dictionary = {e.character: e for e in mmah_dictionary_entries}
    graphics = {e.character: e for e in mmah_graphics_entries}
    hsk_chars = {
        char
        for entry in hsk_entries
        for text in (entry.simplified, _s2t.convert(entry.simplified))
        for char in text
    }
    valid_chars = [c for c in validate(dictionary, graphics) if c in hsk_chars]
    build_database(valid_chars, dictionary, graphics, hsk_entries, output_dir)
