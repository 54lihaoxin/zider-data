# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo contains the data pipeline that produces the reference SQLite database bundled inside the Zider iOS app. It is public to satisfy the copyleft requirements of the upstream data sources. Pipeline scripts are MIT licensed; data files retain their upstream licenses and must not be relicensed.

## Data Sources

| Dataset | Source | License |
|---|---|---|
| HSK vocabulary | [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) | MIT |
| `graphics.txt` | [Make Me A Hanzi](https://github.com/54lihaoxin/makemeahanzi) (fork) | Arphic Public License |
| `dictionary.txt` | [Make Me A Hanzi](https://github.com/54lihaoxin/makemeahanzi) (fork) | LGPL v3+ |

## Structure

- `ziderdata/` — library package: `schema.py` (dataclasses), `encoding.py` (binary codec), `aggregate.py` (build logic), one parser module per source file
- `download.py` — downloads all source data files from GitHub
- `build.py` — runs the full pipeline end-to-end
- `sources/` — raw source data (git-ignored)
- `output/` — final SQLite (git-ignored; distributed as a release)

## Commands

Download all source data:
```
python3 download.py
```

Run the full pipeline (process all sources + build the database):
```
python3 build.py
```

Run all tests:
```
python3 -m unittest discover tests
```

Run a single test:
```
python3 -m unittest tests.test_makemeahanzi_dictionary.TestParseDictionary.test_full_entry
```

## Output

`output/zider.sqlite` is a read-only reference database bundled into the Zider iOS app.
