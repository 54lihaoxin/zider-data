# zider-data

Data pipeline for the [Zider](https://github.com/54lihaoxin/zider) iOS app — a Chinese character and word learning app. This repo is public to satisfy the copyleft requirements of the upstream data sources.

## What this produces

`output/zider.sqlite` — a read-only reference database bundled into the Zider iOS app, covering ~9500 Chinese characters and ~11500 HSK vocabulary words. Character data includes stroke order paths, pinyin, definitions, decomposition, radical, and stroke count. Word data includes HSK levels, pinyin, meanings, classifiers, and parts of speech.

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

## Licenses

Pipeline scripts are MIT licensed. Data files retain their upstream licenses:

| Source | License |
|---|---|
| HSK vocabulary (`complete-hsk-vocabulary`) | [MIT](LICENSES/MIT-complete-hsk-vocabulary.txt) |
| Make Me A Hanzi (`graphics.txt`) | [Arphic Public License](LICENSES/ARPHICPL.TXT) |
| Make Me A Hanzi (`dictionary.txt`) | [LGPL v3+](LICENSES/LGPL-3.0.txt) |
