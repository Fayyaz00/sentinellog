# SentinelLog

SentinelLog is a local Python security log analysis project.

This first step reads a local text log and displays its lines with line numbers.
It uses only Python's standard library and requires no account.

In PowerShell, from this folder, run:

```powershell
py analyze.py sample.log
```

To read another UTF-8 text log, replace `sample.log` with its path. Enclose paths
containing spaces in quotes. Use synthetic or sanitized logs when sharing output.
