# zider-data

Data pipeline for the [Zider](https://github.com/54lihaoxin/zider) iOS app — a Chinese character and word learning app. This repo is public to satisfy the copyleft requirements of the upstream data sources.

## What this produces

`output/zider-data.sqlite` — a read-only reference database bundled into the Zider iOS app, covering ~9500 Chinese characters and ~11500 HSK vocabulary words. Character data includes stroke order paths, pinyin, definitions, decomposition, radical, and stroke count. Word data includes HSK levels, pinyin, meanings, classifiers, and parts of speech.

Pre-built releases are available on the [Releases page](https://github.com/54lihaoxin/zider-data/releases). The latest database can be downloaded directly at:

```
https://github.com/54lihaoxin/zider-data/releases/latest/download/zider-data.sqlite.gz
```

## Usage

```bash
# Download all source data files
python3 download.py

# Run the full pipeline (process all sources + build the database)
python3 build.py

# Run tests
python3 -m unittest discover tests
```

See [CLAUDE.md](CLAUDE.md) for full developer documentation.

## Database schema

### `hsk_words`

One row per HSK vocabulary entry.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-assigned row ID |
| `simplified` | TEXT | Simplified Chinese, e.g. `中国` |
| `frequency` | INTEGER | Corpus frequency rank (lower = more frequent); NULL if unknown |
| `pos` | TEXT | Pipe-separated parts of speech, e.g. `noun\|verb` |
| `hsk_old` | INTEGER | HSK level under the pre-2021 standard (1–6); NULL if not listed |
| `hsk_new` | INTEGER | HSK level under the 2021 standard (1–9); NULL if not listed |
| `hsk_newest` | INTEGER | HSK level under the 2024 standard (1–9); NULL if not listed |

### `hsk_word_forms`

One row per pronunciation/meaning variant. Words with multiple readings have multiple forms.

| Column | Type | Description |
|---|---|---|
| `word_id` | INTEGER FK | References `hsk_words.id` |
| `form_index` | INTEGER | Zero-based position among the word's forms |
| `pinyin` | TEXT | Pinyin with tone marks, e.g. `zhōng guó` |
| `classifiers` | TEXT | Pipe-separated measure words (量词), e.g. `个\|位` |
| `meanings` | TEXT | Pipe-separated English definitions |

Primary key is `(word_id, form_index)`.

### `mmah_characters`

One row per Chinese character.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-assigned row ID |
| `character` | TEXT | The character, e.g. `中` |
| `pinyin` | TEXT | Space-separated readings, e.g. `zhōng guó` |
| `decomposition` | TEXT | Component breakdown using Ideographic Description Characters |
| `radical` | TEXT | Kangxi radical |
| `stroke_count` | INTEGER | Number of strokes |
| `etymology_type_id` | INTEGER FK | References `mmah_etymology_types.id`; NULL if unknown |

### `mmah_etymology_types`

Lookup table for etymology categories.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-assigned |
| `name` | TEXT | Category name, e.g. `pictographic`, `ideographic`, `pictophonetic` |

### `mmah_strokes`

One row per stroke, in stroke order. Paths and medians are stored as compact bit-stream BLOBs — see [Stroke binary format](#stroke-binary-format) below.

| Column | Type | Description |
|---|---|---|
| `character_id` | INTEGER FK | References `mmah_characters.id` |
| `stroke_index` | INTEGER | Zero-based position in stroke order |
| `path` | BLOB | Encoded SVG path (M/L/Q/C/Z commands) |
| `median` | BLOB | Encoded centerline points `[[x, y] …]` for animation |

Primary key is `(character_id, stroke_index)`.

## Stroke binary format

Stroke paths and medians are stored as compact bit streams (MSB first) in the `strokes` table.

### Paths (`strokes.path`)

```
M.x  (11 bits)
M.y  (11 bits)
[ cmd (2 bits)  coord… (11 bits × N) ] …
end  (2 bits = 00)
```

Command codes: `00` = end (Z), `01` = Q (4 coords), `10` = L (2 coords), `11` = C (6 coords).  
All coordinate values are stored as `value + 119` (unsigned). Subtract 119 to recover the signed value.

### Medians (`strokes.median`)

```
[ x (11 bits)  y (11 bits) ] …
```

Point count = `(data.count * 8) / 22`.  
Same coordinate offset: subtract 119 from each value.

### Swift decoder

`BitReader` reads arbitrary-width bit fields MSB first. `decodePath` reconstructs the SVG path string; `decodeMedian` returns an array of `[x, y]` integer points. Both can be used directly with the BLOBs fetched from SQLite.

```swift
struct BitReader {
    private let data: Data
    private var pos = 0

    init(_ data: Data) { self.data = data }

    mutating func read(_ n: Int) -> Int {
        var result = 0, remaining = n
        while remaining > 0 {
            let byteIdx = pos >> 3
            let available = 8 - (pos & 7)
            let take = min(remaining, available)
            result = (result << take) | (Int(data[byteIdx]) >> (available - take) & ((1 << take) - 1))
            pos += take; remaining -= take
        }
        return result
    }
}

func decodePath(_ data: Data) -> String {
    var r = BitReader(data)
    var parts = ["M", "\(r.read(11) - 119)", "\(r.read(11) - 119)"]
    let coords = [0b01: 4, 0b10: 2, 0b11: 6]
    let names  = [0b01: "Q", 0b10: "L", 0b11: "C"]
    while true {
        let cmd = r.read(2)
        guard cmd != 0 else { parts.append("Z"); break }
        parts.append(names[cmd]!)
        for _ in 0 ..< coords[cmd]! { parts.append("\(r.read(11) - 119)") }
    }
    return parts.joined(separator: " ")
}

func decodeMedian(_ data: Data) -> [[Int]] {
    var r = BitReader(data)
    return (0 ..< data.count * 8 / 22).map { _ in [r.read(11) - 119, r.read(11) - 119] }
}
```

## Data Sources and Licenses

Pipeline scripts are MIT licensed. Data files retain their upstream licenses:

| Dataset | Repository | License |
|---|---|---|
| HSK vocabulary | [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) | [MIT](LICENSES/MIT-complete-hsk-vocabulary.txt) |
| Character dictionary (`dictionary.txt`) | [skishore/makemeahanzi](https://github.com/skishore/makemeahanzi) | [LGPL v3+](LICENSES/LGPL-3.0.txt) |
| Character stroke data (`graphics.txt`) | [skishore/makemeahanzi](https://github.com/skishore/makemeahanzi) | [Arphic Public License](LICENSES/ARPHICPL.TXT) |
