# Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The style issues were the easiest. Changing `== None` to `is None`, renaming bySchemeCount to by_scheme_count, adding docstrings and splitting long lines only took a minute each, since the tools tell you the exact line and what's wrong. Replacing os.system with print was also easy, and it fixed a few Bandit warnings at once.

The hardest was getting rid of the global disbursed_total. I couldn't just delete the `global` line because the program needed the total somewhere. I ended up putting everything in a class and calculating the total from the database instead of keeping a separate counter.

The double payment bug was also tricky, mostly because none of the tools found it. I only noticed it while fixing the return statements in disburse(). The actual fix was just one extra check.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Not really. Everything they reported was a real issue, but a couple of warnings were a bit misleading.

Pylint gave C0209 on the SQL line, suggesting an f-string instead of % formatting. If I'd followed that, the SQL injection would still be there. The right fix was a parameterised query, which Bandit's warning pointed towards.

Bandit's B605 warning on os.system even says "seems safe", since the command was a fixed string with no user input. So it wasn't an actual vulnerability yet, more of a warning about a risky pattern.

The bigger problem was what the tools missed. None of them caught that an award could be paid twice.

## 3. How would you integrate static analysis tools into your actual software development workflow?

I'd set up Flake8 and Pylint in VS Code so problems show up while I'm writing code. I'd also add a pre-commit hook that runs all three tools, so badly formatted or unsafe code can't be committed.

For a team project, I'd add them to GitHub Actions so they run on every push and pull request, and fail the build if Bandit finds anything medium or high, or if the Pylint score drops below about 9.5.

I'd still write unit tests as well, since this lab showed the tools can't catch logic bugs like the double payment.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

The Pylint score went from 5.00 to 10.00, and Flake8 and Bandit both show zero issues now. The program still gives the same output, so nothing broke.

The code is safer now. Names with apostrophes don't crash it anymore, the SQL injection is gone, and it doesn't open a shell. It's also more correct: an award can't be paid twice, audit lists aren't shared between calls, and bad amounts are rejected.

It's easier to read too. Every function has a docstring, the names follow PEP 8, and the lines fit on screen. Because of the class and the `__main__` guard, the file can be imported and tested without running the demo.
