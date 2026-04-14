#!/usr/bin/env python3
"""
Caveman Compress CLI

Usage:
    caveman <filepath> [--lang=<code>]
"""

import argparse
import sys
from pathlib import Path

from .compress import compress_file
from .detect import detect_file_type, should_compress
from .i18n import get_lang, t


def print_usage():
    print(t('cli.usage'))


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('filepath', nargs='?', default=None)
    parser.add_argument('--lang', default=None)
    parser.add_argument('-h', '--help', action='store_true')

    args, _ = parser.parse_known_args()

    if args.help or args.filepath is None:
        print_usage()
        sys.exit(0 if args.help else 1)

    # Resolve lang before any output so t() uses correct locale
    _lang = get_lang(cli_arg=args.lang)

    filepath = Path(args.filepath)

    # Check file exists
    if not filepath.exists():
        print(f"❌ {t('cli.file_not_found', file=filepath)}")
        sys.exit(1)

    if not filepath.is_file():
        print(f"❌ {t('cli.not_a_file', file=filepath)}")
        sys.exit(1)

    filepath = filepath.resolve()

    # Detect file type
    file_type = detect_file_type(filepath)

    print(t('cli.detected', type=file_type))

    # Check if compressible
    if not should_compress(filepath):
        print(t('cli.skipping_not_natural'))
        sys.exit(0)

    print(t('cli.compress.starting') + "\n")

    try:
        success = compress_file(filepath)

        if success:
            backup_path = filepath.with_name(filepath.stem + ".original.md")
            print("\n" + t('cli.compress.success'))
            print(t('cli.compress.compressed', file=filepath))
            print(t('cli.compress.original', file=backup_path))
            sys.exit(0)
        else:
            print("\n❌ " + t('cli.compress.failed_after_retries'))
            sys.exit(2)

    except KeyboardInterrupt:
        print("\n" + t('cli.compress.interrupted'))
        sys.exit(130)

    except Exception as e:
        print("\n❌ " + t('cli.compress.error', message=e))
        sys.exit(1)


if __name__ == "__main__":
    main()
