from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DictionaryEntry:
    character: str
    pinyin: list[str] = field(default_factory=list)
    definition: str | None = None
    decomposition: str | None = None
    radical: str | None = None
    etymology: dict[str, Any] | None = None
    matches: list[Any] = field(default_factory=list)


@dataclass
class GraphicsEntry:
    character: str
    strokes: list[str] = field(default_factory=list)
    medians: list[list[list[int]]] = field(default_factory=list)
