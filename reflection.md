# Reflection: Lab 5 Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the style and documentation issues. The tools pointed to the exact line and named the fix:

- `scheme == None` → `scheme is None` (C0121 / E711)
- renaming `bySchemeCount` → `by_scheme_count` (C0103)
- adding docstrings (C0114 / C0116)
- wrapping the long lines (C0301 / E501)

Removing `os.system("echo …")` was also simple once I saw that it only printed a message. Switching to `print` fixed B605, B607, B110 and W0718 together and let me drop the `os` import.

**Hardest:** the issues tied to the program's *state and logic*:

- **The global `disbursed_total` (W0603).** Deleting the `global` line on its own would break the program. I had to decide where the total should live. Keeping a separate counter next to the database meant two copies of the same fact that could disagree. So I moved the connection into a `ScholarshipLedger` class and computed the total from the database (`SUM(amount) WHERE disbursed = 1`). This was a real design change, not a one-line edit.
- **The double-disbursement bug.** No tool reported it. I only found it by reading `disburse()` while fixing the inconsistent return (R1710) next to it. Calling `disburse(1)` three times counted the award three times. The fix itself was small (check the `disbursed` flag), but noticing the bug was the hard part.
- **SQL injection (B608).** The fix (`?` placeholders) is short, but I had to be careful. Pylint's C0209 on the *same line* suggests an f-string, and following that advice would have kept the injection. The right fix makes C0209 irrelevant, rather than doing what C0209 literally asks.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no outright false positives. Every message pointed at something real. A few were **misleading or overlapping**:

- **Pylint C0209 (`consider-using-f-string`) on line 10** was the clearest example. The line *was* using `%` formatting, so the message is technically correct. But following the advice would have kept the SQL injection. The real problem was string-building SQL at all, which Bandit's B608 reported correctly.
- **Bandit B605 (`start_process_with_a_shell`)** describes itself as *"Seems safe, but may be changed in the future"*. The command was a fixed string with no user input, so it could not be exploited at the time. This is a "risky pattern" warning, not a live vulnerability. I fixed it anyway because the shell call was pointless.
- **Duplicate reports.** Flake8 E501 and Pylint C0301 both flag long lines, with different limits (79 and 100). E711 and C0121 both flag `== None`, and B110 and W0718 both flag the bare `except`. These are not false positives, but they inflate the issue count.

The reverse problem, **false negatives**, mattered more. None of the three tools noticed that the same award could be disbursed twice, or that negative or float amounts were accepted. Static analysis checks patterns. It cannot know that a scholarship should only be paid once.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Local development:** run Flake8 and Pylint in the editor (the VS Code Python extension can show them inline) so issues appear while typing. Add a `pre-commit` hook that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r .`, so code that fails cannot be committed.
- **Continuous integration:** add a GitHub Actions job that installs the pinned tool versions from `requirements.txt` and runs all three tools on every push and pull request. Fail the build on any Bandit Medium/High finding, any Flake8 error, or a Pylint score below the threshold, so the checks run even if someone skips the local hook.
- **Configuration:** keep shared settings in `pyproject.toml` / `setup.cfg` (for example, agree on one line-length limit so Flake8 and Pylint stop disagreeing). Allow a specific rule to be disabled only with an inline comment that explains why (for example `# nosec B608 - table name is a constant`), rather than turning rules off globally.
- **Alongside other checks:** static analysis does not replace tests or code review. The double-disbursement bug shows this. A unit test such as "disbursing twice must not change the total" would have caught it, and the tools did not.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Measured results:** Pylint went from **5.00/10 to 10.00/10**. Flake8 went from 6 issues to 0, and Bandit from 4 issues (1 Medium) to 0. The demo output (`50000 None` / `1 50000` / `archiving awards`) is unchanged, so the behaviour was kept.
- **Security:** names with apostrophes (`O'Brien`) used to crash the program, and a crafted name could insert a forged, already-disbursed award. Both are now stored safely as plain data. The program no longer starts a shell.
- **Correctness and robustness:**
  - An award can no longer be paid out twice.
  - Audit lists are no longer shared between `grant()` calls.
  - Invalid amounts raise a clear `ValueError`.
  - The disbursed total comes from the database, so it can never disagree with the records.
- **Readability and maintainability:**
  - Every function has a docstring.
  - Names follow PEP 8.
  - The SQL statements are short enough to read without scrolling.
  - The state is held in a `ScholarshipLedger` object instead of module-level globals.
  - The `if __name__ == "__main__"` guard means the module can be imported and unit-tested without running the demo, and each test can create its own fresh ledger.
