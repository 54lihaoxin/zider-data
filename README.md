# zider-data

Data pipeline for the [Zider](https://github.com/54lihaoxin/zider) iOS app — a Chinese character and word learning app. This repo is public to satisfy the copyleft requirements of the upstream data sources.

## What this produces

`output/zider.sqlite` — a read-only reference database bundled into the Zider iOS app, covering ~3000 most common Chinese characters with stroke order paths, pinyin, definitions, frequency rank, and HSK level.

## Licenses

Pipeline scripts are MIT licensed. Data files retain their upstream licenses:

| Source | License |
|---|---|
| HSK vocabulary (`complete-hsk-vocabulary`) | [MIT](LICENSES/MIT-complete-hsk-vocabulary.txt) |
| Make Me A Hanzi (`graphics.txt`) | [Arphic Public License](LICENSES/ARPHICPL.TXT) |
| Make Me A Hanzi (`dictionary.txt`) | [LGPL v3+](LICENSES/LGPL-3.0.txt) |

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
