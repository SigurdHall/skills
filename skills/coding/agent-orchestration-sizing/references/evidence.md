# Evidence behind the sizing rules

Dated observations. Add a line when a run says something about shape, tier or effort.

## 30.09.2026, tertialrapport session (ultracode on, every agent inherited Opus 5.5)

- **Proposal round with judges, colour palette:** 8 agents, 0.75 M tokens, 9 min. Three of four independent proposals landed on the same palette. The proposal stage could have been two Sonnet generators.
- **Two palette workflows stopped mid-run:** the user redirected the brief twice within minutes ("for kjedelig", then "bare UiT-farger"). Both runs were wasted. Wait for the decision or show an inline mock-up when the user is steering.
- **Palette workflow v4:** 9 agents, 1.40 M tokens, 16 min. The user changed direction twice more afterwards. The final palette came from an inline contrast calculation over seven candidates plus two renders, in a few tool calls. That was a narrow parameter search, so it belonged inline.
- **Silver notebook change plus three-lens review:** 5 agents, 0.78 M tokens, 28 min. The production reviewer found that `overwriteSchema` would erase column comments every night and let upstream schema changes through, and it was fixed with `mergeSchema`. This is the production criterion paying off.
- **Desktop round with one subagent:** 0.25 M tokens, 15 min, 3 reloads, 0 DAX. One coherent sequential job with serialized side effects, so one subagent was right.
- **Earlier the same day:** parallel verification agents with full DEFINE blocks pushed Fabric capacity to 100 %. There must be one external-system runner per round (see `fabric-cu-glatting` in ws_okonomi).
- **Open hypothesis (not decided):** when the user has fixed the design and the change is only measures and text, the builder's own tests may be enough, and a separate reviewer adds cost without adding information. The user raised this as an assumption on 30.09.2026. Test it: run such builds without a reviewer and record here whether the post-deploy checks or the user found defects that a reviewer would have caught.
- **User rules stated this day:** do not use Haiku until it is on the same version level as the others, and do not use workflows for everything.
- **Hypothesis test 1, Godkjent-mode build without reviewer:** 1 Opus builder, 0.39 M tokens, 23 min, with a decided design (measures, texts, slicer settings). After deploy, every Godkjent field and the O4 sums matched the answer key on the first run. The only defect was that the builder's own test query exceeded the 1 GB memory limit and had to be split. A code reviewer would not have caught that before running it. This is one data point for the hypothesis.
- **monotoneX build, 01.10.2026:** the prompt spelled out the full D3 curveMonotoneX algorithm (slope formulas, Bézier control points, file list, checks), and the agent still inherited Opus at session effort. The user pointed out that a prompt this specific is Sonnet work, and that Opus and Fable should not need specs this detailed. Rule added: match prompt specificity to the tier.

## 01.10.2026, ledelsesrapport session (ultracode on)

- **Tier audit:** six workflows from 12:00 ran 23 agents on Opus and 10 on Sonnet. Sonnet ran only where `model: 'sonnet'` was set: source search, mapping readers, proposal generators. Every builder, fixer and Fabric runner had no `model` and inherited Opus. About 14 of the 23 were Sonnet work: builders with full specs (C1–C8, silver for søknader), fixers, runners executing a given query plan, and method agents that were told the method. The user noticed ("bare opus agenter"). Causes: the table row "Implementation with judgment → inherit (opus)" won over "arbeidsordre → Sonnet"; the Workflow tool's default "omit model" was followed; ultracode was read as "Opus everywhere". Fixed in the table and rules: never omit `model`, builders and fixers on Sonnet, Opus for reviewers and judges.
- **Production rule broken:** the silver build for søknader (schema change) ran on Opus. The rule is Sonnet builds, one Opus check.
- **Duplicate agent:** answering a workflow builder's question with SendMessage resumed it as a second background agent. Two copies edited `tr_maal.py` at once until the copy was stopped with TaskStop.
- **Agents refusing the task:** in a resumed workflow, the data, method and judge agents refused because the user's latest message was an unrelated question. Quoting the user's request verbatim in the prompt fixed it.
- **Production review paid off again:** the Opus reviewer of the søknad silver branch found no blockers and flagged a changed periodisation rule for explicit acceptance, plus seven minor gaps (an empty comment, the 2099 deadline placeholder, a missing phase guard). All were fixed before deploy.
- **After the fix, same day:** three workflows ran with the new rules.
  - R2a, knappetips and toppteksten: 1 Sonnet builder and 1 Opus reviewer. Clean in the first round.
  - M2, søknad measures and palette in the model: 1 Sonnet builder and 1 Opus reviewer. Clean in the first round, with every answer-key number matched against the live model.
  - R2b, palette, the Søknader view and a new report page: 4 Sonnet and 4 Opus. Two Sonnet builders, then a Sonnet fixer, then an Opus fixer after the second failed review (the escalation rule), and 3 Opus reviews. The last review was clean.
  - Sonnet builders with full specs held up, and the escalation step was needed only for the largest round.
- **02.10.2026, session documentation from an 800k-character transcript:** a workflow was chosen on the "beyond one context" criterion. 7 Sonnet readers (one per transcript chunk, fixed findings schema), 1 Opus synthesizer, 1 Sonnet writer, 1 Opus reviewer and 1 Sonnet fixer: 11 agents, about 1.8M subagent tokens, 38 minutes.
  - The Opus reviewer found 15 real problems the writer missed. The worst were a systematic quote-mark corruption that broke every Markdown table, quotes that existed only in compacted summaries and not in user messages, and two decisions stated as final that the user had left open.
  - The main loop still had to correct facts that changed while the workflow ran (a deploy that finished after launch). Give documentation workflows a cut-off time, or re-check the open-items section against the final state before committing.
