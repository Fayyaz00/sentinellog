"""Summarize severity levels in a local text log."""

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# Keep the report readable even when an error repeats thousands of times.
MAX_EXAMPLES = 5

# Match the sample format: timestamp, severity, service, and message.
LOG_LINE = re.compile(
    r"""
    ^\d{4}-\d{2}-\d{2}               # Date
    [ T]\d{2}:\d{2}:\d{2}            # Time
    (?:\.\d+)?Z?\s+                  # Optional fractions and UTC marker
    (?P<level>INFO|WARNING|WARN|ERROR)\s+
    (?P<service>\S+)\s+              # Service name
    (?P<message>.+?)\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


@dataclass
class EventGroup:
    count: int = 0
    example_lines: list[int] = field(default_factory=list)

    def record(self, line_number: int) -> None:
        self.count += 1
        if len(self.example_lines) < MAX_EXAMPLES:
            self.example_lines.append(line_number)


@dataclass
class Summary:
    """Counts and source locations collected from a log file."""

    total: int = 0
    counts: Counter[str] = field(default_factory=Counter)
    errors: dict[str, EventGroup] = field(default_factory=lambda: defaultdict(EventGroup))
    failed_logins: dict[str, EventGroup] = field(default_factory=lambda: defaultdict(EventGroup))
    unrecognized_count: int = 0
    unrecognized_examples: list[tuple[int, str]] = field(default_factory=list)


def analyze_lines(lines: Iterable[str]) -> Summary:
    """Count recognized events and retain unrecognized lines for review."""
    summary = Summary()
    for line_number, line in enumerate(lines, start=1):
        summary.total += 1
        original_line = line.rstrip("\r\n")
        match = LOG_LINE.match(original_line)
        if not match:
            summary.unrecognized_count += 1
            if len(summary.unrecognized_examples) < MAX_EXAMPLES:
                summary.unrecognized_examples.append((line_number, original_line))
            continue

        level = match.group("level").upper()
        if level == "WARNING":
            level = "WARN"
        summary.counts[level] += 1

        message = match.group("message")
        if level == "ERROR":
            summary.errors[message].record(line_number)
        if "invalid credentials" in message.casefold():
            summary.failed_logins[match.group("service")].record(line_number)
    return summary


def print_summary(summary: Summary, failed_login_threshold: int = 5) -> None:
    """Display counts, grouped errors, and lines the parser could not read."""
    print(f"Lines analyzed: {summary.total}")
    for level in ("INFO", "WARN", "ERROR"):
        print(f"{level}: {summary.counts[level]}")
    print(f"Unrecognized: {summary.unrecognized_count}")
    print("\nError messages:")
    if not summary.errors:
        print("  None")
    sorted_errors = sorted(
        summary.errors.items(),
        key=lambda item: (-item[1].count, item[0]),
    )
    for message, error in sorted_errors:
        references = ", ".join(str(number) for number in error.example_lines)
        print(f"  {error.count}  {message} (example lines: {references})")

    print(f"\nFailed-login findings (threshold: {failed_login_threshold}):")
    findings = [
        (service, events)
        for service, events in summary.failed_logins.items()
        if events.count >= failed_login_threshold
    ]
    if not findings:
        print("  None")
    for service, events in sorted(findings, key=lambda item: (-item[1].count, item[0])):
        references = ", ".join(str(number) for number in events.example_lines)
        print(f"  {service}: {events.count} matching lines (example lines: {references})")

    if summary.unrecognized_count:
        print("\nUnrecognized line examples:")
        for line_number, original_line in summary.unrecognized_examples:
            print(f"  {line_number}: {original_line}")
        if summary.unrecognized_count > len(summary.unrecognized_examples):
            print("  Additional unrecognized lines are available in the source file.")


def positive_integer(value: str) -> int:
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("must be a positive integer")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a local log file.")
    parser.add_argument("file", type=Path, help="Path to a UTF-8 text log")
    parser.add_argument(
        "--failed-login-threshold",
        type=positive_integer,
        default=5,
        help="minimum matching lines per service to report (default: 5)",
    )
    args = parser.parse_args()

    try:
        with args.file.open(encoding="utf-8") as log_file:
            summary = analyze_lines(log_file)
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"Could not read {args.file}: {error}\n")

    print_summary(summary, args.failed_login_threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
