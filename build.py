import argparse
from pathlib import Path

from ziderdata.aggregate import run as aggregate
from ziderdata.hsk import parse as parse_hsk
from ziderdata.mmah_dictionary import parse as parse_dictionary
from ziderdata.mmah_graphics import parse as parse_graphics

DEFAULT_MAKEMEAHANZI_DIR = Path('sources/makemeahanzi')
DEFAULT_HSK_DIR = Path('sources/complete-hsk-vocabulary')
DEFAULT_OUTPUT_DIR = Path('output')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full zider-data pipeline.')
    parser.add_argument('--hsk-dir', type=Path, default=DEFAULT_HSK_DIR)
    parser.add_argument('--makemeahanzi-dir', type=Path, default=DEFAULT_MAKEMEAHANZI_DIR)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    hsk_entries = parse_hsk(args.hsk_dir / 'complete.json')
    mmah_dictionary_entries = parse_dictionary(args.makemeahanzi_dir / 'dictionary.txt')
    mmah_graphics_entries = parse_graphics(args.makemeahanzi_dir / 'graphics.txt')
    aggregate(hsk_entries, mmah_dictionary_entries, mmah_graphics_entries, args.output_dir)
