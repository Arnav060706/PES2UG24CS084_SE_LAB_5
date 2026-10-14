# Issues Found

I ran Pylint, Flake8 and Bandit on `scholarship_disbursement.py`. Line numbers are from the original file. The original reports are in `reports/before/`.

| Issue | Type | Line(s) | Description | Fix Approach |
| --- | --- | --- | --- | --- |
| SQL injection (Bandit B608) | Security - High | 10 | The INSERT query was built with % string formatting, so the student name went straight into the SQL. A name like O'Brien crashed the program, and a crafted name could add a fake award that was already marked as paid. | Used a parameterised query with ? placeholders. |
| Mutable default argument (Pylint W0102) | Bug - High | 9 | `audit=[]` is created once and shared between calls, so the second grant() call still had the first student in its list. | Changed the default to None and create a new list inside the function. |
| Award can be paid twice (not caught by any tool) | Logic bug - High | 15-21 | disburse() never checked if an award was already paid. Calling disburse(1) three times added the amount to the total three times. | Check the disbursed column first and return None if it's already paid. |
| Global variable (Pylint W0603) | Design - Medium | 6, 16 | disbursed_total was a global updated with the `global` keyword. It kept a separate copy of data that was already in the database. | Moved everything into a ScholarshipLedger class and calculate the total from the database with SUM(). |
| os.system call (Bandit B605, B607) | Security - Medium | 26 | archive() opened a shell just to run `echo`. Not dangerous right now, but risky if the command ever includes user input. | Replaced it with a plain print(). |
| Empty except block (Bandit B110, Pylint W0718) | Error handling - Medium | 27-28 | `except Exception: pass` hides any error. | Removed the try/except since there's nothing left in it that can fail. |
| Inconsistent returns (Pylint R1710) | Code quality - Medium | 15-21 | disburse() returned a value on one path and nothing on the other. | Added an explicit `return None`. |
| No __main__ guard | Design - Low | 45 | main() ran whenever the file was imported. | Wrapped it in `if __name__ == "__main__":`. |
| Comparing to None with == (Pylint C0121, Flake8 E711) | Style - Low | 32 | Should use `is None`. | Changed to `if scheme is None:`. |
| Function name not snake_case (Pylint C0103) | Style - Low | 31 | bySchemeCount doesn't follow PEP 8. | Renamed to by_scheme_count. |
| Missing docstrings (Pylint C0114, C0116) | Documentation - Low | 1, 9, 15, 24, 31, 37 | No module or function docstrings. | Added docstrings everywhere. |
| Lines too long (Pylint C0301, Flake8 E501) | Style - Low | 5, 10, 17, 19, 34 | Several lines were over the length limit. | Split the SQL strings over multiple lines. |

I also added a check so grant() rejects negative, zero or decimal amounts, since those were being accepted before.

## Before and after

| Tool | Before | After |
| --- | --- | --- |
| Pylint | 5.00/10 | 10.00/10 |
| Flake8 | 6 issues | 0 issues |
| Bandit | 4 issues (1 medium, 3 low) | 0 issues |

The program still prints the same output as before:

```text
50000 None
1 50000
archiving awards
```
