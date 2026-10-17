# Research Gateway — volunteer review playbook (pilot)

**Status:** Operational guidance only; not a replacement for [METHOD](METHOD.md), [WORKFLOW](WORKFLOW.md), [CONTROLS](CONTROLS.md) or owner authority.

**Goal:** Contributors can find a bounded question, submit evidence, and receive peer critique without the owner personally routing every early step. GitHub Issues and forked PRs are sufficient; no paid platform, new CI, or AI write access is required.

## Volunteer workflow

1. **Choose freely.** Investigate your own original question, choose an optional [starter problem](RESEARCH_OPPORTUNITIES.md), or critique a precise claim in a research note. No assignment or permission to begin independent work is required.
2. **Submit without a prerequisite issue.** Open a [research evidence or original proposal issue](https://github.com/holland202/principia-artificialis/issues/new?template=research_evidence.yml) or a forked PR. For existing claims, pin commit/line and actual observations; for a new idea, label ORIGINAL PROPOSAL / NO PRIOR PA SOURCE and planned checks NOT RUN.
3. **Triage (any willing volunteer).** Check for duplication, scope, safe instructions, provenance and missing data. Ask narrow questions; do not treat a comment as scientific approval.
4. **Review (another volunteer where feasible).** Trace the argument, attempt a separately permitted existing check, or propose a counterexample. Record who reviewed, exact commands/outputs if run, limitations and disagreements. A same-code re-run differs from an independent implementation.
5. **Owner gate only for official actions.** No owner permission is needed to start independent research, propose a topic, submit an issue, or open a forked PR. Changes to canonical methods, formal PA research registration, official study execution, merges, releases and PA publication require Chad Holland or an explicitly authorized maintainer. Peer feedback does not confer those permissions.

## Suggested triage markers (text only; not installed GitHub labels)

| Marker | Meaning |
|---|---|
| NEW | Received, not yet checked |
| NEEDS DETAILS | Source pin, method, scope or raw evidence missing |
| READY FOR REVIEW | Sufficiently specific for peer inspection |
| REVIEWED — SOURCE ONLY | Argument/source inspected; nothing executed |
| REVIEWED — TESTED | Actual test run with named operator and raw evidence |
| UNRESOLVED / REFUTED (KEPT) | Preserve contrary evidence or unresolved uncertainty |
| AWAITING OWNER GATE | A concrete authorization or governance decision is pending |
| CLOSED WITH EVIDENCE | A scoped disposition exists, linked and preserved |

These operational signals are not formal prediction verdicts. For authoritative terms see METHOD.md §4.

## Minimum reviewer checklist

- Is the claim pinned to an exact revision and identifiable line?
- Does the report distinguish source review, a self-test, a re-run, and an independent implementation?
- Are commands, environments, observed exits, stderr/stdout and source hashes present if code ran?
- Could the instrument return the opposite result under its actual policy? Does the sabotage check recognize the intended failure, not an unrelated exception?
- Are negative, contradictory and missing outcomes retained?
- Are attribution, citations and AI involvement accurate?
- Are private data and reserved scientific cases protected?
- Does the response avoid implying authority to freeze, merge, execute or publish?

## Sample feedback (adapt manually; never auto-post)

**Clarification:** “Thanks for the specific lead. Please include the exact source commit, file/line, and whether it was inspected or executed. If executed, attach commands, raw outputs and exits.”

**Useful refutation:** “The negative result remains in the record. It supports [narrow observation], not [broader claim]. The next independent check is [small specific test].”

**Owner gate:** “The scoped evidence was reviewed. A separate maintainer decision is required for [specific merge / research freeze / run]. This review alone is not approval.”

## Four-week pilot evaluation

Count only observations with inspectable timestamps and links: new source-pinned contributors; starter issues receiving meaningful questions; findings reaching a disposition without owner triage; preserved negative outcomes; and elapsed time to substantive review when measurable. Record missing/ignored issues too.

There is **no guaranteed reviewer coverage**, target performance, automatic triage or validation. Volunteer participation must not be described as independently replicated science. Decide whether to continue or expand only after examining the actual pilot record.

**Access and privacy:** [Grok governance Issue #57](https://github.com/holland202/principia-artificialis/issues/57) describes a *not configured* read-only concept, not active permission. No AI is authorized to post automatically. Contributors need only normal GitHub accounts.

*AI-assisted initial draft (OpenAI GPT-6); published as owner-authorized W9 documentation, not a verified research result.*
