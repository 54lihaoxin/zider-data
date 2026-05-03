from __future__ import annotations

# Decode functions serve as format documentation for the Swift decoder.

_COORD_BITS = 11
_COORD_OFFSET = 119  # shifts coordinate range [-119, 1023] to [0, 1142]

# 2-bit command codes — M (start) and Z (end) are implicit; not stored
_CMD_ENCODE = {'Q': 0b01, 'L': 0b10, 'C': 0b11}
_CMD_DECODE = {0b01: 'Q', 0b10: 'L', 0b11: 'C'}
_CMD_NCOORDS = {'M': 2, 'Q': 4, 'L': 2, 'C': 6}
_END_BITS = 0b00


class _BitWriter:
    """Write integers as arbitrary-width bit fields, MSB first, into a byte buffer."""

    def __init__(self) -> None:
        self._acc = 0
        self._nbits = 0
        self._buf = bytearray()

    def write(self, value: int, nbits: int) -> None:
        self._acc = (self._acc << nbits) | (value & ((1 << nbits) - 1))
        self._nbits += nbits
        while self._nbits >= 8:
            self._nbits -= 8
            self._buf.append((self._acc >> self._nbits) & 0xFF)

    def flush(self) -> bytes:
        if self._nbits:
            self._buf.append((self._acc << (8 - self._nbits)) & 0xFF)
        return bytes(self._buf)


class _BitReader:
    """Read arbitrary-width bit fields, MSB first, from a byte buffer."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def read(self, nbits: int) -> int:
        result = 0
        remaining = nbits
        while remaining:
            byte_idx = self._pos >> 3
            bit_offset = self._pos & 7
            available = 8 - bit_offset
            take = min(remaining, available)
            result = (result << take) | ((self._data[byte_idx] >> (available - take)) & ((1 << take) - 1))
            self._pos += take
            remaining -= take
        return result


def encode_path(path: str) -> bytes:
    """Encode SVG path string to compact bit-stream binary.

    Format (MSB first):
      M.x (11 bits), M.y (11 bits),
      repeating: cmd (2 bits: 01=Q  10=L  11=C) + N×coord (11 bits each),
      end marker (2 bits: 00).
    Coordinates stored as (value + 119) unsigned, covering source range [-119, 1023].
    M and Z are implicit and not stored.
    """
    tokens = path.split()
    writer = _BitWriter()
    i = 0
    while i < len(tokens):
        cmd = tokens[i]; i += 1
        if cmd == 'Z':
            writer.write(_END_BITS, 2)
            break
        ncoords = _CMD_NCOORDS[cmd]
        if cmd != 'M':
            writer.write(_CMD_ENCODE[cmd], 2)
        for _ in range(ncoords):
            writer.write(round(float(tokens[i])) + _COORD_OFFSET, _COORD_BITS)
            i += 1
    return writer.flush()


def decode_path(data: bytes) -> str:
    """Decode compact bit-stream binary back to SVG path string."""
    reader = _BitReader(data)
    parts = ['M']
    for _ in range(2):
        parts.append(str(reader.read(_COORD_BITS) - _COORD_OFFSET))
    while True:
        cmd_bits = reader.read(2)
        if cmd_bits == _END_BITS:
            parts.append('Z')
            break
        cmd = _CMD_DECODE[cmd_bits]
        parts.append(cmd)
        for _ in range(_CMD_NCOORDS[cmd]):
            parts.append(str(reader.read(_COORD_BITS) - _COORD_OFFSET))
    return ' '.join(parts)


def encode_median(median: list[list[int]]) -> bytes:
    """Encode stroke median points to compact bit-stream binary.

    Format: repeating (x: 11 bits, y: 11 bits), coordinates offset by 119.
    Point count = (len(data) * 8) // 22
    """
    writer = _BitWriter()
    for x, y in median:
        writer.write(round(x) + _COORD_OFFSET, _COORD_BITS)
        writer.write(round(y) + _COORD_OFFSET, _COORD_BITS)
    return writer.flush()


def decode_median(data: bytes) -> list[list[int]]:
    """Decode compact bit-stream binary back to list of [x, y] points."""
    reader = _BitReader(data)
    n = (len(data) * 8) // (_COORD_BITS * 2)
    return [
        [reader.read(_COORD_BITS) - _COORD_OFFSET, reader.read(_COORD_BITS) - _COORD_OFFSET]
        for _ in range(n)
    ]
