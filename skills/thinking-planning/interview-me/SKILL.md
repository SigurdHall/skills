---
name: interview-me
description: Use when the user has a rough, unformed idea, problem, or request and wants help turning it into a concrete brief through one-question-at-a-time conversation — extracting the real goal, constraints, scope, and success criteria before any plan or critique exists. Triggers: "interview me about this", "help me think this through", "what should I be asking myself", "flesh this idea out", "help me figure out what I actually want". Also Norwegian phrasing: still meg spørsmål om dette, hjelp meg tenke gjennom dette, jeg har bare en løs idé, avklar dette med meg, hva bør jeg avklare før jeg starter. Understand and elicit first — do not critique or pressure-test; switch to grill-me once a concrete plan exists to stress-test.
---

# Interview Me

Use this before there is a plan to critique — when the user has a vague goal,
problem, or request and needs it turned into something concrete enough to act
on or hand off.

Core protocol:

- Ask one question at a time. Wait for the answer before the next branch.
- Each question should narrow the goal, a constraint, a scope boundary, or a
  success criterion — not test the user's thinking.
- Do not evaluate, praise, or critique answers. Reflect them back briefly and
  move to the next gap.
- If the answer can be found by inspecting local files, code, docs, or data,
  inspect them instead of asking.
- Follow dependencies between questions; do not jump randomly across topics.

Question targets:

- What is the actual goal, and who is it for?
- What triggered this now — what problem or gap does it close?
- What is explicitly out of scope?
- What does "done" look like, and how would you know it worked?
- What constraints are fixed (deadline, budget, tooling, format, audience)
  versus flexible?
- What decisions can wait, and what must be decided now?

Stop interviewing once goal, scope, constraints, and success criteria are
each answerable in one sentence. Then summarize into a short brief: goal,
scope (in/out), constraints, success criteria, open questions. Offer to hand
that brief to a more specific skill next.

Related skills: [grill-me](../grill-me/SKILL.md) for adversarial
pressure-testing once a plan exists, [narrative-design](../narrative-design/SKILL.md)
for structuring the resulting communication, [skill-design](../skill-design/SKILL.md)
for turning a recurring brief into a reusable skill.
