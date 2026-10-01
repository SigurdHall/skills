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
