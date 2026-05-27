---
name: readable-python-code
description: Write, simplify, review, refactor, or explain Python code for readability and maintainability. Use when the user asks for Python script, notebook helper, ETL utility, smoke test, .env-driven test script, command-line tool, logging/error handling, type hints, docstrings, PEP 8/PEP 257, beginner-friendly explanation, rydd opp i Python-kode, forklar linje for linje, or make Python code clearer without changing behavior.
---

# Readable Python Code

Use this when the user asks for Python that is easy to read, understand, review, teach, or maintain.

## Sources To Apply

Use the principles from:

- PEP 8: readability and consistency, naming, layout, comments, imports.
- PEP 257: docstrings for modules, scripts, functions, and classes.

Do not treat style rules as a substitute for clarity. Prefer the simplest code that makes the data flow obvious.

## Rewrite Workflow

1. Read the existing code before editing.
2. Identify the main user-facing story: what inputs are read, what work is done, what output is printed.
3. Split code into small named functions when it clarifies the story.
4. Use descriptive names over clever abbreviations.
5. Keep secrets and environment-specific values outside the code.
6. Add short comments only where they explain intent, edge cases, or non-obvious behavior.
7. Add a module docstring that explains purpose, required environment variables, and how to run when useful.
8. Validate with a no-write syntax check if `__pycache__` writes are undesirable.

## Style Rules

- Use `snake_case` for functions, variables, and modules.
- Use `UPPER_CASE` for constants.
- Put standard-library imports first, then third-party imports, then local imports.
- Prefer explicit return values from functions.
- Prefer `pathlib.Path` for local paths.
- Prefer `with` statements for files and network responses.
- Prefer `raise RuntimeError("clear message") from error` when wrapping low-level errors.
- Keep line length reasonable; break long expressions where it improves scanning.
- Avoid global mutable state except constants.

## Code Section Headers

Use short section headers in beginner-friendly scripts and utility files when
they make the file easier to scan. Prefer plain comment headers over decorative
blocks.

Good section headers:

```python
# Configuration
# Environment
# Tableau API calls
# Script entry point
```

Use headers to separate real conceptual sections, not every function. Keep them
short, stable, and concrete. Do not use large ASCII banners or noisy separators.

## Comments And Docstrings

Use docstrings for:

- Module purpose and required setup.
- Public functions and scripts where the reader benefits from a one-sentence summary.
- Non-obvious command-line behavior, environment variables, files, and side effects.

Use comments for:

- Why a workaround is needed.
- Why an edge case is handled.
- Why a security-sensitive choice is made.

Avoid comments that repeat the code:

```python
# Bad: Increment x by one.
x += 1
```

Prefer intent:

```python
# Tableau redirects must keep POST; urllib's default redirect can turn it into GET.
```

## Beginner-Friendly Test Scripts

For simple smoke tests:

1. Put setup constants at the top.
2. Put `.env` loading in a small function.
3. Put validation of required settings in a small function.
4. Put the external API call in one function with clear error messages.
5. Put the high-level sequence in `main()`.
6. End with:

```python
if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Script failed: {error}", file=sys.stderr)
        raise SystemExit(1)
```

## Validation Commands

No-write syntax check:

```powershell
python -B -c "import ast, pathlib; ast.parse(pathlib.Path('script.py').read_text(encoding='utf-8')); print('Syntax OK')"
```

Run script without writing bytecode:

```powershell
python -B script.py
```

If a repo uses Ruff, Black, or pytest, prefer its existing commands instead of adding new tooling.

## Review Checklist

- Can a reader describe the script flow after reading `main()`?
- Are function names verbs or clear noun phrases?
- Are secrets only read from environment variables or secure config?
- Are errors actionable without exposing secrets?
- Are comments explaining intent, not restating syntax?
- Is the code runnable with minimal setup?
