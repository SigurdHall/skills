---
name: readable-python-code
description: Write, simplify, review, or explain Python scripts and notebooks for data and statistics work. Use to prevent unnecessary complexity growth in new code and rewrites, keep data flow visible, and preserve behavior with familiar names and short direct comments. Not a mandate to redesign application or library architecture.
---

# Readable Python Code

Write code that people used to Python, R, and statistical data work can follow
without a software engineering background. Prefer visible data flow over clever
or compact code. Follow the user's language and the target project's conventions;
use the Norwegian examples below for Norwegian data work.

## Complexity Contract

Apply these rules to code added or changed for the task. Preserve required existing
interfaces and project conventions; do not redesign unrelated code to satisfy this
skill. Explicit task requirements take precedence. Identify any required exception
and its reason in the final response; do not silently relax a rule.

- Handle the stated inputs and existing documented contracts. Do not invent new input cases, optional modes, configuration options, or fallbacks. Missing information is not a non-null or uniqueness guarantee. Ask only when an unresolved assumption changes the result or write behavior; otherwise state the assumption and proceed without speculative branches.
- Do not introduce classes, factories, registries, decorators, configuration frameworks, or generic wrappers unless a current requirement or existing interface needs them. A possible future use is not a requirement.
- Keep a new standalone analysis in one script or notebook. Do not introduce a package, module split, or new dependency unless the task cannot be completed clearly with the existing environment. Preserve existing module boundaries during rewrites.
- Do not introduce custom retry loops, caching, concurrency, or optimization infrastructure without a stated operational requirement or measured bottleneck. Use straightforward efficient library operations; bounded network timeouts are allowed.
- Let unexpected errors propagate. Catch a specific exception only for required recovery, actionable context, or cleanup that a context manager cannot provide. Do not add custom exception classes, catch-all handlers, silent defaults, or logging setup to a standalone analysis. Preserve required existing logging and recovery.
- Keep adjustable non-secret settings as plain constants near the top. Keep secrets outside the code. Do not add a CLI, settings object, or `main()` wrapper unless required by the invocation or existing interface. Notebook cells do not need an entry-point guard.

## Functions And Complexity Budgets

- Extract a function only to remove repeated logic, isolate a calculation that needs independent testing, or name a distinct transformation stage. State which purpose any new helper serves. A wrapper that only renames a library call does not qualify without an interface requirement.
- Pass dependencies explicitly. A parameter is valid even when one call site passes one value; do not move inputs into globals to reduce the parameter count. A call inside a loop or callback can provide real reuse.
- Add optional parameters, defaults, `*args`, or `**kwargs` only for required call patterns or existing interfaces. Do not generalize a helper for hypothetical callers.
- Budget for new or changed functions: at most four parameters and cyclomatic complexity eight. Use existing lint tooling to measure complexity when available. Keep at most three nested control-flow suites; the function body does not count, and `elif` is at the same level as `if`.
- Treat 120 source lines as a review threshold for a standalone script or notebook, not a reason to stop a valid task. Count with `splitlines()`, including comments and blank lines; for notebooks count only code-cell source, summed across cells.
- When a budget is exceeded, first simplify without changing behavior. If required logic still exceeds it, retain the clear implementation and report the measure and concrete reason. Do not increase an already over-budget function's complexity unless required by the task and explained.
- Never meet a budget by removing useful names or spacing, packing statements onto one line, bundling unrelated parameters into a dict, duplicating logic, or moving branches out of functions to evade measurement. Inspect top-level and notebook control flow too.

## Work Sequence

1. Read the existing code and applicable project instructions. Identify inputs, required transformations, outputs, and write semantics. For rewrites, note the original source-line count and relevant complexity measures available from existing tools.
2. Implement the smallest change that satisfies the task. Keep data flow sequential and visible. Preserve table selection, types, null semantics, keys, ordering, metadata, and append versus overwrite unless the task explicitly changes them.
3. Validate assumptions where they become relevant. Check input contracts at reads; check transformation invariants after the operation that can break them. A join may need a cardinality or total reconciliation check even when inputs were validated. Do not add checks unrelated to the required result.
4. Keep writes explicit and easy to find near the end, with destination and write mode visible. Do not force multiple required outputs into one write or remove staging needed for correctness. Rewrites preserve existing side-effect order.
5. Verify the requested result with the relevant existing checks or a small controlled fixture. Then make a removal pass for unused code, speculative branches, duplicate checks, wrappers, and redundant comments. Preserve required invariants and explanations. Removing nothing is a valid outcome.
6. Re-run relevant verification after the final edit, including deletions. If a removal breaks correctness, restore what is needed and verify again. Do not run writes against live destinations merely to validate a readability edit.

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
- Follow the Complexity Contract for error handling; preserve the original cause when adding context.
- Keep line length reasonable; break long expressions where it improves scanning.
- Shared variables between notebook cells are normal. Do not introduce classes, configuration frameworks, or one-line helper functions just to hide those variables.
- Follow the function rules and budgets above. Fewer lines or functions alone do not establish improved readability.

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

Use a brief docstring when it explains a non-obvious contract, setup requirement,
or side effect; skip boilerplate module headers and obvious docstrings. Follow
PEP 8 and PEP 257 where applicable. Prefer type hints at function boundaries when
they clarify inputs and outputs. Preserve useful existing hints; do not introduce
generic type machinery without an interface requirement.

## Validation Commands

No-write syntax check:

```powershell
python -B -c "import ast, pathlib; ast.parse(pathlib.Path('script.py').read_text(encoding='utf-8')); print('Syntax OK')"
```

Run script without writing bytecode:

```powershell
python -B script.py
```

If a repo uses Ruff, Black, or pytest, prefer its existing commands instead of adding
new tooling or changing repository-wide settings. Report unmeasured complexity as
unmeasured, not as a passing lint check. Syntax and style checks do not prove that
filtering, grouping, joins, totals, or output order are correct.

When a behavioral check is needed, use representative controlled data and assert
the requested result on the same artifact that was linted. For a monthly account
summary, include multiple accounts, repeated rows per account, and another period;
check filtering, sums, and descending order. Do not accept a token scan or the
presence of `print` as evidence that the task is solved. Say when the target runtime
or data was unavailable and which behavior remains unverified.

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

## Completion Report

Keep the response proportional to the change. For code writes and rewrites, report:

- Verification actually run and any remaining runtime or data limitation.
- Source lines before and after a rewrite; for new code, before and after the removal pass. List what was removed, or say nothing unnecessary remained.
- Added files, dependencies, helpers, and input-handling branches, with the current requirement or function purpose for each addition. If none were added, say so briefly.
- Any budget exceedance or contract exception, including its reason. Do not label manual inspection or self-reported compliance as automated enforcement.

For explanation-only or review-only tasks, report findings directly without claiming
an implementation, removal pass, or execution that did not happen.
