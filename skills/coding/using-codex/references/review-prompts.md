# Rescue as a general reviewer

`task` without `--write` runs read-only through the same execution path as
`adversarial-review`, so it gets subagents — **and** it accepts `--effort`,
which `adversarial-review` does not. For anything that is not a git diff,
`task` is the stronger review tool.

```bash
node "$CODEX_PLUGIN/scripts/codex-companion.mjs" task \
  --effort xhigh \
  --background \
  "<prompt>"
```

Omit `--write`. Never add it for a review.

## The five parts of a review prompt

A weak prompt produces agreeable summary. Every review prompt needs:

1. **Scope** — exact paths. Not "the project".
2. **Standard** — what to judge against: a spec, an acceptance criterion, a
   constraint, a policy. Without this Codex invents its own bar.
3. **Output shape** — findings with severity and location, most severe first.
4. **Prohibitions** — do not edit, do not rewrite, do not restate the plan
   back, do not agree by default.
5. **Stop condition** — say "insufficient information" instead of guessing.

## Patterns

### Plan or architecture review

> Review `docs/SUPERPLAN.md` sections 8–10 against the constraint that no
> agent may hold organizational authority it was not released with. List
> every place the plan grants implicit authority, contradicts itself, or
> depends on an unstated assumption. Severity per finding, most severe
> first. Do not propose a rewrite. If a section is ambiguous rather than
> wrong, say so and quote the ambiguity.

### Solution or approach review

> We chose <approach> for <problem>. Constraints: <list>. Read <paths>.
> Name the failure modes this approach has that an alternative would not.
> Identify which of our stated constraints the approach actually satisfies
> and which it only appears to. Do not endorse; assume we are wrong and try
> to show it.

### Execution review — did we do what we claimed?

> The claim is: <claim>. The evidence offered is <paths/commands>. Verify
> the claim strictly against that evidence. For each part, answer
> CONFIRMED, UNSUPPORTED, or CONTRADICTED, with the specific line or output
> that decides it. Do not accept intent as evidence of completion.

### Document review — strategy, decision memo, contract

> Review <path> as a hostile reader who must act on it. List every place
> where the document is unactionable, where two readers would reasonably
> act differently, or where a commitment lacks an owner or a date. Quote
> the text for each finding.

## Reading the result back

Codex output is evidence, not a verdict. Before relaying:

- Check whether the finding is true in the actual files, not just plausible.
- Say which findings you agree with and which you do not, and why.
- Never present an unverified Codex claim as confirmed.
