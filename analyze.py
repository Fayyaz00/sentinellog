"""Read a local text log and display its lines."""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Read a local log file.")
    parser.add_argument("file", type=Path, help="Path to a .log or .txt file")
    args = parser.parse_args()

    try:
        with args.file.open(encoding="utf-8") as log_file:
            for line_number, line in enumerate(log_file, start=1):
                print(f"{line_number}: {line.rstrip()}")
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"Could not read {args.file}: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
