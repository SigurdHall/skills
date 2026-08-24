# Adversarial Review

Mandatory after Create Plan and Update Plan. An independent model attacks the plan; the authoring agent never grades its own output.

1. Announce - State in one line which plan file is being reviewed and that it goes to Codex `gpt-5.6-sol` at `xhigh`, before spending quota
2. Dispatch - Invoke the `codex:codex-rescue` subagent with `--model gpt-5.6-sol --effort xhigh` and without `--write` (review only, no edits). If the codex plugin is unavailable in the current harness, run `codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh` directly
3. Frame Adversarially - Instruct the reviewer to challenge the approach, architecture decisions, tradeoffs, assumptions, phase sequencing, and omissions in `PLAN_FILE` - not just implementation defects. Pass the plan file path and the original `USER_PROMPT` so the reviewer knows the intent
4. Triage Findings - For each finding, explicitly accept or reject it with a one-line reason
5. Revise - Apply accepted findings to the plan, append the current ISO timestamp to `modified`, and record an Amendments entry summarizing the review outcome
6. Report - Summarize the findings, what was accepted and rejected, and the resulting plan changes
