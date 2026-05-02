import argparse
import urllib.request
from pathlib import Path

SOURCES = [
    {
        'url': 'https://raw.githubusercontent.com/54lihaoxin/makemeahanzi/master/dictionary.txt',
        'dest': 'makemeahanzi/dictionary.txt',
    },
    {
        'url': 'https://raw.githubusercontent.com/54lihaoxin/makemeahanzi/master/graphics.txt',
        'dest': 'makemeahanzi/graphics.txt',
    },
]

DEFAULT_SOURCES_DIR = Path('sources')


def download(sources_dir: Path, force: bool) -> None:
    for source in SOURCES:
        dest = sources_dir / source['dest']
        if dest.exists() and not force:
            print(f'Skip {dest} (already exists, use --force to re-download)')
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f'Downloading {source["url"]} ...')
        urllib.request.urlretrieve(source['url'], dest)
        print(f'  -> {dest}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download source data files.')
    parser.add_argument('--sources-dir', type=Path, default=DEFAULT_SOURCES_DIR)
    parser.add_argument('--force', action='store_true', help='Re-download existing files')
    args = parser.parse_args()
    download(args.sources_dir, args.force)
