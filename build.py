import argparse
from pathlib import Path

from ziderdata.aggregate import run as aggregate
from ziderdata.hsk import parse as parse_hsk
from ziderdata.mmah_dictionary import parse as parse_dictionary
from ziderdata.mmah_graphics import parse as parse_graphics
from ziderdata.tang_poems import parse as parse_tang_poems
from ziderdata.qian_jia_shi import parse as parse_qian_jia_shi

DEFAULT_HSK_DIR = Path('sources/complete-hsk-vocabulary')
DEFAULT_MAKEMEAHANZI_DIR = Path('sources/makemeahanzi')
DEFAULT_TANG_POEMS_PATH = Path('sources/chinese-poetry/tangshisanbaishou.json')
DEFAULT_QIAN_JIA_SHI_PATH = Path('sources/chinese-poetry/qianjiashi.json')
DEFAULT_OUTPUT_DIR = Path('output')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full zider-data pipeline.')
    parser.add_argument('--hsk-dir', type=Path, default=DEFAULT_HSK_DIR)
    parser.add_argument('--makemeahanzi-dir', type=Path, default=DEFAULT_MAKEMEAHANZI_DIR)
    parser.add_argument('--tang-poems', type=Path, default=DEFAULT_TANG_POEMS_PATH)
    parser.add_argument('--qian-jia-shi', type=Path, default=DEFAULT_QIAN_JIA_SHI_PATH)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    hsk_entries = parse_hsk(args.hsk_dir / 'complete.json')
    mmah_dictionary_entries = parse_dictionary(args.makemeahanzi_dir / 'dictionary.txt')
    mmah_graphics_entries = parse_graphics(args.makemeahanzi_dir / 'graphics.txt')
    tang_poem_entries = parse_tang_poems(args.tang_poems)
    qian_jia_shi_entries = parse_qian_jia_shi(args.qian_jia_shi)
    aggregate(hsk_entries, mmah_dictionary_entries, mmah_graphics_entries, tang_poem_entries, qian_jia_shi_entries, args.output_dir)
