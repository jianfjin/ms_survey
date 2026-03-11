from importlib import import_module


def main() -> int:
    run = import_module("ms_survey.cli").run
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
