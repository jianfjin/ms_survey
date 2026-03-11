import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ms-survey")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    return parser


def run() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.version:
        from ms_survey import __version__

        print(__version__)
    return 0
