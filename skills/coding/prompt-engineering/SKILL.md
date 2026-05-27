---
name: prompt-engineering
description: Improve, critique, rewrite, or design prompts for LLMs and agent workflows. Use when the user asks to forbedre en prompt, skrive bedre instruks, lage systemprompt, review/critique a prompt, make a prompt more precise, add constraints, add examples, define output format, create eval criteria, reduce hallucination, or convert an ad hoc prompt into a reusable prompt artifact for finance, BI, SQL, Power BI, Python, public-sector work, or model-agnostic prompt libraries.
---

# Prompt Engineering

## Workflow

1. Ask for the prompt if the user has not provided it.
2. Identify the intended task, audience, inputs, output format, constraints, and failure modes.
3. Critique the prompt briefly across:
   - clarity
   - specificity
   - context
   - output format
   - edge cases
   - what not to do
4. Rewrite the prompt in a portable form that does not depend on hidden system instructions.
5. Explain the most important changes and any trade-offs.

## Defaults

Prefer prompts that include:

- role or operating context
- concrete goal
- relevant domain context
- expected inputs
- strict output structure
- explicit constraints
- missing-data behavior
- an honesty clause when judgment is required

For finance, BI, SQL, ERP, and public-sector work, require traceability and prohibit invented data, columns, metrics, policies, or source references.

## Output

Return:

1. Short diagnosis
2. Improved prompt
3. Why the changes matter

Keep prose concise. Use Norwegian for explanation unless the user asks otherwise; write the prompt itself in the language that best fits its target use.
