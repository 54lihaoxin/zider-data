from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any



@dataclass
class HskEntry:
    simplified: str
    frequency: int | None = None
    pos: list[str] = field(default_factory=list)
    hsk_new: int | None = None
    hsk_newest: int | None = None
    hsk_old: int | None = None
    forms: list[HskForm] = field(default_factory=list)


@dataclass
class HskForm:
    pinyin: str | None = None
    meanings: list[str] = field(default_factory=list)
    classifiers: list[str] = field(default_factory=list)


@dataclass
class MmahDictionaryEntry:
    character: str
    pinyin: list[str] = field(default_factory=list)
    definition: str | None = None
    decomposition: str | None = None
    radical: str | None = None
    etymology: dict[str, Any] | None = None
    matches: list[Any] = field(default_factory=list)


@dataclass
class MmahGraphicsEntry:
    character: str
    strokes: list[str] = field(default_factory=list)
    medians: list[list[list[int]]] = field(default_factory=list)
