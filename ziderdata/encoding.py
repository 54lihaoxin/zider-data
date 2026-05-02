from __future__ import annotations

import struct

# Decode methods in this file are test-only, but they also serves as format documentation.

_CMD_ENCODE = {'M': 0, 'Q': 1, 'L': 2, 'C': 3, 'Z': 4}
_CMD_DECODE = {v: k for k, v in _CMD_ENCODE.items()}
_CMD_NCOORDS = {'M': 2, 'Q': 4, 'L': 2, 'C': 6, 'Z': 0}


def encode_path(path: str) -> bytes:
    """Encode SVG path string to binary.

    Format: repeating (cmd: uint8, coords: int16 LE...) until end of data.
    Command map: M=0, Q=1, L=2, C=3, Z=4
    """
    tokens = path.split()
    buf = bytearray()
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        n = _CMD_NCOORDS[cmd]
        buf.append(_CMD_ENCODE[cmd])
        for j in range(n):
            buf.extend(struct.pack('<h', round(float(tokens[i + 1 + j]))))
        i += 1 + n
    return bytes(buf)


def decode_path(data: bytes) -> str:
    """Decode binary path back to SVG path string."""
    parts = []
    i = 0
    while i < len(data):
        cmd = _CMD_DECODE[data[i]]
        n = _CMD_NCOORDS[cmd]
        parts.append(cmd)
        for j in range(n):
            parts.append(str(struct.unpack_from('<h', data, i + 1 + j * 2)[0]))
        i += 1 + n * 2
    return ' '.join(parts)


def encode_median(median: list[list[int]]) -> bytes:
    """Encode stroke median points to binary.

    Format: repeating (x: int16 LE, y: int16 LE).
    Point count = len(data) // 4
    """
    buf = bytearray()
    for x, y in median:
        buf.extend(struct.pack('<hh', round(x), round(y)))
    return bytes(buf)


def decode_median(data: bytes) -> list[list[int]]:
    """Decode binary median back to list of [x, y] points."""
    return [
        list(struct.unpack_from('<hh', data, i))
        for i in range(0, len(data), 4)
    ]
