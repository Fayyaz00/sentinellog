# SentinelLog

SentinelLog is a local Python security log analysis project.

SentinelLog summarizes severity levels, groups identical error messages, and
shows their original line numbers. It uses only Python's standard library and
requires no account.

In PowerShell, from this folder, run:

```powershell
py analyze.py sample.log
```

To read another UTF-8 text log, replace `sample.log` with its path. Enclose paths
containing spaces in quotes. Use synthetic or sanitized logs when sharing output.

The initial parser expects one event per line in this format:

```text
2026-01-10 14:35:05 ERROR auth-service Database connection failed
```

It recognizes INFO, WARN (or WARNING), and ERROR levels. Lines that do not match
the format, including blank lines and continuation lines, are counted separately.
The report shows up to five examples of unrecognized lines and five source line
numbers per error message; the complete lines remain in the original file.
Error messages are grouped by exact message
text across services; no security conclusion is inferred from the severity.
Other log formats may require a different parser.

The file is read one line at a time, and repeated events retain only their count
and a few example locations. Memory still grows with the number and length of
distinct error messages; this version is intended for local log files, not
unbounded or high-cardinality log streams.

Run the tests with:

```powershell
py -m unittest
```
