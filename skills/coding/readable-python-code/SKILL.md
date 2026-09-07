---
name: readable-python-code
description: Write, simplify, review, or explain readable Python scripts and notebooks for data and statistics work. Use for clear data flow, familiar variable names, short direct comments, simpler ETL or smoke tests, and removing unnecessary abstraction or premature optimization while preserving behavior.
---

# Readable Python Code

Write code that people used to Python, R, and statistical data work can follow
without a software engineering background. Prefer visible data flow over clever
or compact code. Follow the user's language and the target project's conventions;
use the Norwegian examples below for Norwegian data work.

## Sources To Apply

Use the principles from:

- PEP 8: readability and consistency, naming, layout, comments, imports.
- PEP 257: docstrings for modules, scripts, functions, and classes.

Do not treat style rules as a substitute for clarity. Prefer the simplest code that makes the data flow obvious.

## Rewrite Workflow

1. Read the existing code before editing.
2. Identify the main user-facing story: what inputs are read, what work is done, what output is printed.
3. Keep simple scripts and notebooks sequential. Extract a function when it removes real repetition or makes a difficult step easier to understand.
4. Use descriptive names over clever abbreviations.
5. Keep secrets and environment-specific values outside the code.
6. Add short, direct comments where they help the reader find a step or understand a reason or assumption.
7. Preserve behavior during readability edits, including table selection, metadata, and append versus overwrite. Treat a functional fix as a separate, explicit change.
8. Validate with a no-write syntax check if `__pycache__` writes are undesirable.

## Style Rules

- Use `snake_case` for functions, variables, and modules.
- Use familiar technical names such as `client_secret`, `headers`, `profile_path`, `source_schema`, and `df`. Do not translate established terms literally just because comments are Norwegian.
- Norwegian business names such as `antall_rader`, `budsjett`, or `regnskap` are fine when natural. Choose names for the reader and the existing code; do not force every identifier into one language. Keep library APIs and external field names unchanged.
- Use `UPPER_CASE` for constants.
- Put standard-library imports first, then third-party imports, then local imports.
- Use ordinary assignments and loops when they make the steps easier to follow. Simple comprehensions are fine; split nested expressions and long method chains when intermediate names help.
- Prefer explicit return values from functions.
- Prefer `pathlib.Path` for local paths.
- Prefer `with` statements for files and network responses.
- Add error handling where it gives a useful next step or necessary cleanup. Preserve the original cause when wrapping an error; avoid catch-all wrappers around every operation.
- Keep line length reasonable; break long expressions where it improves scanning.
- Shared variables between notebook cells are normal. Do not introduce classes, configuration frameworks, or one-line helper functions just to hide those variables.
- Optimize a demonstrated bottleneck. Do not add caching, concurrency, or extra layers without a concrete need.

## Notebook And Script Structure

For data notebooks, show the flow from setup to result:

1. Brief purpose and required setup.
2. Settings the reader may need to change.
3. Connection and input data.
4. Selection and necessary checks.
5. Processing and saving.
6. Short result summary.

These are useful divisions, not a required cell count. Keep source selection and
checks visible before writes. The reader should be able to inspect intermediate
results without following a chain of helper calls.

Small scripts can follow the same sequence. Use `main()` and a command-line
entry point when the script needs them; do not impose that structure on a
notebook or split a short smoke test into a function for every step.

## Code Section Headers

Use short section headers in beginner-friendly scripts and utility files when
they make the file easier to scan. Prefer plain comment headers over decorative
blocks.

Good section headers:

```python
# Innstillinger
# Tilkobling
# Velger tabeller
# Lagrer data
```

Use headers to separate real conceptual sections, not every function. Keep them
short, stable, and concrete. Do not use large ASCII banners or noisy separators.

## Comments And Docstrings

Match the user's voice. In Norwegian, use short action phrases such as
`Henter`, `Velger`, and `Lagrer`. Prefer a direct note over a formal sentence
about what "we" are going to do. Do not polish the user's wording into a more
formal register.

Too formal:

```python
# Vi henter bare tabeller fra den valgte delingen og kildeskjemaet.
```

Preferred:

```python
# Henter kun tabeller fra valgte skjema
```

Drop filler such as "Vi skal nå", "Formålet med dette er", and "Det er viktig
å merke seg". Keep a reason when it matters:

```python
# Beholder tidligere innlastinger for å kunne sammenligne uttrekk
```

A short comment can label a useful block. Avoid narrating each statement or
turning simple code into a tutorial. Brevity must not hide a meaningful
condition, unit, side effect, or reason for a workaround.

Use a brief docstring for a function or script when it adds useful context about
inputs, outputs, setup, or side effects. Skip obvious docstrings and decorative
comment banners. Type hints should clarify an interface, not overwhelm simple
data handling.

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

- Can a reader describe the data flow by reading the notebook or script from top to bottom?
- Are function names verbs or clear noun phrases?
- Does each abstraction make the code easier to follow?
- Are secrets only read from environment variables or secure config?
- Are errors actionable without exposing secrets?
- Do comments sound like short working notes in the user's voice?
- Is necessary meaning preserved without restating obvious syntax?
- Are data contracts and write behavior unchanged unless the task calls for a change?
- Is the code runnable with minimal setup?
