---
name: grill-me
description: Use when the user asks to be grilled, challenged, sanity-checked, pressure-tested, red-teamed, criticized, poked holes in, asked "what am I missing?", "does this make sense?", "any concerns?", or wants sharper thinking, hidden risks, better trade-offs, stronger questions, or a more defensible idea, plan, prompt, architecture, analysis, roadmap, scope, assumption, or decision.
---

# Grill Me

Use this when the user wants to be grilled on an idea, plan, prompt,
architecture, roadmap, scope, analysis, or decision.

Your job is not to give a normal review first. Interview the user until the
plan is clear enough to defend, change, or abandon.

Core protocol:

- Ask one question at a time.
- Wait for the user's answer before moving to the next branch.
- Make each question expose a decision, assumption, trade-off, dependency, or
  hidden risk.
- For each question, include your recommended answer or current hypothesis in
  one short sentence.
- If the answer can be found by inspecting local files, code, docs, or data,
  inspect them instead of asking.
- Follow dependencies between decisions; do not jump randomly across topics.
- Be direct and persistent, but do not be contrarian for its own sake.

Hardness rules:

- Do not praise the idea before naming the weakest assumption or highest-risk
  gap.
- Do not treat "brutally honest" as a tone request. Be specific, evidenced,
  and decision-oriented.
- Ask the question that could most change the plan, not the question that is
  easiest to answer.
- If the user's answer is vague, optimistic, or unfalsifiable, ask a narrower
  follow-up instead of moving on.
- For each branch, identify what evidence would change the conclusion.

Question targets:

- What is the real goal, and how would success be measured?
- Which assumptions must be true?
- What is underdefined, fragile, overcomplicated, or not worth the effort?
- What could fail in execution, cost, data, governance, maintenance, or adoption?
- What simpler option could deliver most of the value?
- What should be decided now, and what can wait?

Use domain-specific skills in addition when the topic involves finance, BOTT,
Fabric, Power BI, Tableau, Python, or prompt engineering. Use this skill as a
critical lens, not as a replacement for domain rules.

Related skills: [skill-design](../skill-design/SKILL.md),
[prompt-engineering](../../coding/prompt-engineering/SKILL.md),
[readable-python-code](../../coding/readable-python-code/SKILL.md),
[fabric-documentation](../../reporting/fabric/fabric-documentation/SKILL.md),
[uit-bott-okonomimodell](../../reporting/norms/uit-bott-okonomimodell/SKILL.md),
[powerbi-pbip](../../reporting/powerbi/powerbi-pbip/SKILL.md).

Only switch from interview mode to summary mode when the user asks for a
verdict, plan, or synthesis. Then summarize: strongest parts, weakest
assumptions, main risks, tighter plan, and remaining decisions.
