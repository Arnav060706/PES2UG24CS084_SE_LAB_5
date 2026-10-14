# Issues Found: `scholarship_disbursement.py`

Tools: Pylint 4.1.3, Flake8 7.4.1, Bandit 1.9.4 (Python 3.12.7, run inside `.venv`).
Line numbers refer to the **original** file. Raw reports from that run are in [`reports/before/`](reports/before/),
and the reports for the final file are `pylint_report.txt`, `flake8_report.txt` and `bandit_report.txt`.

## Issue table

Sorted by severity, high and medium first. Every row is **fixed** in the final file.

| # | Issue | Type | Line(s) | Description | Fix Approach |
| --- | --- | --- | --- | --- | --- |
| 1 | SQL injection (Bandit **B608**, CWE-89) | Security, **High** (Bandit: Medium severity) | 10 | `grant()` builds the `INSERT` with `%`-formatting, so the student and scheme values are pasted straight into the SQL. A name like `O'Brien` crashes with `OperationalError`, and a crafted name like `x', 'Merit', 1, 1); --` inserts a forged award that is already marked as disbursed. Pylint also flags the line (C0209, C0301). | Use a parameterised query: `VALUES (?, ?, ?, 0)` with `(student, scheme, amount)` passed separately, so SQLite treats the values as data and never as SQL. |
| 2 | Mutable default argument (Pylint **W0102**) | Bug, **High** | 9, 11 | `audit=[]` is created once, when the function is defined, and shared by every call. `grant("A",…)` followed by `grant("B",…)` returns `['A', 'B']` both times, so audit trails leak between calls. | Default to `audit=None` and create a new list inside the function (`if audit is None: audit = []`). |
| 3 | Same award can be disbursed more than once (found by reading the code, no tool flags it) | Logic bug, **High** | 15-21 | `disburse()` never checks the `disbursed` flag. Calling `disburse(1)` three times adds the amount to `disbursed_total` three times, so the office pays out money twice. | Select `disbursed` along with `amount` and return `None` if the award is already paid. The total is now computed from the database (`SUM(amount) WHERE disbursed = 1`), so it cannot drift. |
| 4 | Global mutable state (Pylint **W0603**, C0103) | Design / Maintainability, **Medium** | 6, 16, 20 | The module-level `disbursed_total` is changed through `global`. It duplicates data that already lives in the database, so the two can disagree. Pylint also wants module-level names in UPPER_CASE. | Remove the global. Put the connection inside a `ScholarshipLedger` class and derive the total with a `disbursed_total()` query. |
| 5 | Shell command via `os.system` (Bandit **B605**, **B607**, CWE-78) | Security, **Medium** | 26 | `archive()` starts a shell just to print a message, and relies on whatever `echo` comes first on `PATH`. If the string is ever built from user input, this becomes command injection. | Replace it with `print("archiving awards")`. No subprocess or shell is needed. This also drops the unused `os` import. |
| 6 | Exception swallowed with `except Exception: pass` (Bandit **B110**, Pylint **W0718**) | Error handling, **Medium** | 27-28 | Any failure in `archive()` is silently ignored, which hides real errors such as a failed archive. | Remove the `try/except`. Once the shell call is gone nothing in the block can fail, and future errors will surface instead of being hidden. |
| 7 | Inconsistent return statements (Pylint **R1710**) | Code quality, **Medium** | 15-21 | `disburse()` returns an amount on one path and falls off the end (implicit `None`) on the other, which makes the "not found" result easy to miss. | Return `None` explicitly using a guard clause: `if row is None or row[1]: return None`. |
| 8 | No input validation on `amount` | Robustness, **Medium** | 9-10 | Negative, zero or float amounts were accepted (`%d` silently truncated `10.7` to `10`). | Raise `ValueError` unless `amount` is a positive `int`. |
| 9 | Code runs on import (no `__main__` guard) | Design, **Low** | 45 | `main()` is called at module level, so importing the module (for tests, for example) runs the demo and writes to the DB. | Wrap it in `if __name__ == "__main__": main()`. |
| 10 | Comparison to `None` with `==` (Pylint **C0121**, Flake8 **E711**) | Style / Correctness, **Low** | 32 | `scheme == None` can be fooled by objects that override `__eq__`. PEP 8 says to use identity. | `if scheme is None:` |
| 11 | Non-snake_case function name (Pylint **C0103**) | Style, **Low** | 31, 41 | `bySchemeCount` breaks PEP 8 naming. | Renamed to `by_scheme_count` and updated the caller. |
| 12 | Missing docstrings (Pylint **C0114**, **C0116**) | Documentation, **Low** | 1, 9, 15, 24, 31, 37 | No module docstring and no function docstrings. | Added a module docstring and docstrings for the class and every method and function. |
| 13 | Lines too long (Pylint **C0301**, Flake8 **E501**) | Style, **Low** | 5, 10, 17, 19, 34 | Five lines go over 79 characters (Flake8) or 100 characters (Pylint). | Split the SQL strings with implicit string concatenation and wrap the call arguments. |
| 14 | Old-style `%` string formatting (Pylint **C0209**) | Style, **Low** | 10 | Pylint suggests an f-string here. | Not applicable once fixed: a parameterised query is the correct fix here, **not** an f-string, which would still be injectable. |

## Results

| Tool | Before | After |
| --- | --- | --- |
| Pylint | **5.00/10** (16 messages) | **10.00/10** (0 messages) |
| Flake8 | 6 issues (5 × E501, 1 × E711) | 0 issues |
| Bandit | 4 issues (1 Medium, 3 Low) | 0 issues |

The program still does its job, and the demo output is the same before and after:

```text
50000 None
1 50000
archiving awards
```

> When the original's output was redirected to a file or pipe, `archiving awards` printed *first*. This is because
> `os.system` started a separate process that wrote its output immediately, while Python's own `print` output
> was still buffered and only appeared later.
> Using `print` keeps the output in program order.

Screenshots of every tool run before and after the fixes are in [`screenshots/`](screenshots/).
