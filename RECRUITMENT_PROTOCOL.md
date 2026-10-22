# Challenge-Based Recruitment Protocol

**Status: IN EFFECT (pilot).** Merged from the owner's account in PR #63 (2026-10-18); recruitment reopened by owner direction on 2026-10-22. *(Superseded status line, kept verbatim: "DRAFT — proposed by AI, pending owner review. Not in effect until the owner merges it.")*
**Scope:** how a stranger becomes a trusted research contributor across holland202's public repositories, by passing a
challenge instead of asking for access. Principia Artificialis is the default home. The protocol sits beside
[JOIN_RESEARCH.md](JOIN_RESEARCH.md), which stays open to anyone. It is the evidence route into Stage 1 of the
[Contributor Trust Path](CONTRIBUTOR_TRUST_PATH.md). It does not change [METHOD.md](METHOD.md),
[WORKFLOW.md](WORKFLOW.md) or [CONTROLS.md](CONTROLS.md).

## Participation terms — voluntary, unpaid, curiosity-driven

**This is free, voluntary, unpaid research for people who enjoy exploring ideas, learning, testing claims, and contributing to shared knowledge.** There are no fees, dues, required working hours, mandatory assignments, or employment offers. People choose whether to participate, what to investigate independently, and when to stop.

**The only recognition offered is accurate public credit and, when a contribution is accepted and the contributor gives written permission, publication of that contribution in the relevant repository.** Publication is subject to evidence review, contributor consent, licensing permissions, and maintainer acceptance; neither publication nor a positive finding is guaranteed. No salary, consulting fee, stipend, expense reimbursement, equity, profit-sharing, royalties, commercial partnership, or future payment is offered or promised.

Participation does not surrender anyone's intellectual property or authorize use of unpublished designs beyond the rights explicitly granted. Contributors who require financial compensation or commercial terms should agree on those terms separately **before** undertaking that work; none are implied by this invitation.

## 1. Why a challenge

The open gateway lets anyone start. It does not tell us who can be trusted with review, blind testing or scoped write
access. A conversation or CV cannot answer that, but one piece of checkable work can.

The model is the first independent evaluation this program received. A reviewer
([sunny-kavixo](contributions/sunny-kavixo/)) followed these steps:

1. picked a public tool on his own (vacuity_lint);
2. wrote his own test cases instead of re-running ours;
3. sent an evidence package with source files, commands and outputs;
4. reported what did *not* work as plainly as what did.

We re-ran every case against the published repository and the results matched exactly. His package's sources were
byte-identical to the published code. He then gave written consent to publication and chose his own credit wording. The
next step offered to him was to write **blind tests** for a fix he did not build. This protocol turns that sequence into
a repeatable path.

## 2. The filter in one sentence

**We admit people whose claims survive reproduction and who report their own failures. We decline people whose claims
do not reproduce, who hide negatives, or who want endorsement more than scrutiny.**

## 3. Stages

| Stage | What the candidate does | What we do | Exit |
|---|---|---|---|
| C0 Choose | Picks one challenge from the [menu](challenges/entry/README.md), or proposes their own against any listed public repo | Nothing. No sign-up, no permission. | They open an entry issue |
| C1 Declare | Opens an [entry-challenge issue](.github/ISSUE_TEMPLATE/entry_challenge.yml). States the claim they will test, the commit they pinned and what result would prove them wrong, **before** running anything | Checks that the declaration is falsifiable and in scope. Replies "in scope" or names what is missing. | Declaration accepted |
| C2 Submit | Delivers an evidence package (§4) | — | Package received |
| C3 Reproduce | — | A maintainer re-runs the package against the **published** repository at the pinned commit and compares byte-for-byte where possible. The result is posted as MATCH, PARTIAL (names what differs) or NO MATCH. | Reproduction posted |
| C4 Respond | Answers concrete questions. May revise **once**, and the revision is appended, never overwritten. | Re-checks only what changed | Disposition (§5) |
| C5 Consent & record | Gives written consent to publication and supplies their own credit wording and profile link, or declines publication | Publishes an Independent Evaluation record (§7) in `contributions/<handle>/` using their exact wording | Record merged |
| C6 Blind round | Writes test cases and expected outcomes for a fix someone else built, sealed before the fix is shown to them (§6) | Runs the sealed cases. The builder never sees or edits them. | Trust Path Stage 1 → 2 evidence |

There is no deadline at any stage. Silence is not failure. An abandoned challenge simply stays open.

## 4. Evidence package (minimum)

1. **Pinned source:** repository, commit SHA, files and lines.
2. **Declared claim and falsifier**, copied from C1 unchanged. Any change is listed as a dated deviation.
3. **Environment:** OS, runtime, dependency versions and device.
4. **Exact commands, raw stdout/stderr and exit codes.** Attach them; do not summarize.
5. **Hashes** (SHA-256) of any files the candidate wrote and of the outputs.
6. **Observation kept separate from interpretation.**
7. **What failed, what was not checked, and what would change the conclusion.**
8. **AI use:** the model and version, what it did, and what the human checked themselves. Using AI is allowed; hiding it
   is disqualifying (§8).

## 5. Dispositions

The decision is published on the issue. It names the evidence and leaves room to disagree.

- **ACCEPTED — reproduced.** Reproduction matches, and negatives and limits are disclosed. This counts as the
  "substantive auditable contribution" for Trust Path Stage 1. **A refuted hypothesis can be ACCEPTED.** We are judging
  the contribution, not whether the result was positive.
- **ACCEPTED — partial.** The core reproduces and named parts do not. The differences are recorded, not argued away.
- **NOT YET.** Something specific is missing (commands, pinned commit, raw output). The decision lists exactly what, and
  the candidate can resubmit.
- **DECLINED.** One or more disqualifiers in §8 applied. The reason is stated narrowly and factually, with no public
  accusations beyond the observed facts. One appeal with new evidence is allowed.

## 6. Sealed challenges (how weak or fabricated entries get caught)

Some menu items carry a **sealed answer**. Before the challenge is posted, the owner writes the expected finding and
commits only its SHA-256 to [challenges/entry/SEALED.md](challenges/entry/SEALED.md). The plaintext is revealed after
the challenge closes, so anyone can check the answer was fixed in advance.

Three kinds:

- **Planted-defect.** A real, documented defect at a pinned commit. A correct entry finds it and shows reproducible
  evidence.
- **Null-answer (honesty probe).** The correct finding is "no defect at this commit" or "cannot be determined from the
  available evidence". An entry that reports a dramatic defect here without reproducible evidence fails, and so does one
  that cannot show its work. This catches invented findings and AI output pasted without checking. The menu never says
  which items are null-answer.
- **Open.** No sealed answer. The candidate's own question against a listed repo, judged by reproduction alone.

Sealing rules:

1. The owner, or a constructor who is neither the builder of the code under test nor Claude, writes and seals answers.
   Claude may suggest candidate challenges but never writes sealed answers. The program's rule is that the builder of
   something does not grade it.
2. Each sealed item records: challenge ID, pinned commit, the SHA-256 of `ID|commit|answer|salt`, and the date.
3. A sealed answer is never edited. If it was wrong, that is recorded as a refutation of the challenge itself and kept.

## 7. Independent Evaluation record (template)

Filed as `contributions/<handle>/IE-<n>_<short-title>.md`:

```
# IE-<n>: <title>
Evaluator: <name/handle exactly as they asked to be credited> — <profile link they supplied>
Credit wording (evaluator's own words): "<verbatim>"
Consent: written consent to publish received <date>, via <channel>. Consent text kept privately by the owner.
Challenge: <menu ID or OPEN>   Repository: <repo>   Pinned commit: <sha>
Declared claim and falsifier (C1): <verbatim>
Evidence package: <files + SHA-256>
Maintainer reproduction (C3): MATCH | PARTIAL | NO MATCH — <commands, outputs, environment>
What held / what did not / what was not checked: <...>
Disposition: <§5 label> — <date>
Independence statement: The evaluator's own run is the independent evidence. Re-runs by maintainers or by AI systems
confirm reproducibility, not independence.
Provenance: <AI participation, if any> → human validation (<level actually performed>) → human editing → human
responsibility (<owner>).
```

## 8. Disqualifiers (any one leads to DECLINED)

1. **Fabricated or unreproducible results**, including after the one allowed revision.
2. **Undisclosed AI-generated work** presented as the candidate's own hands-on work.
3. **Hidden negatives**: deleting or omitting failures that the evidence shows they ran into.
4. **Testing outside scope**: attacks on infrastructure, accounts, CI secrets, other users or live services, or any
   security testing of a repository beyond its own published challenge rules or a written agreement. sovereign-veritas
   in particular has its own [CHALLENGE.md](https://github.com/holland202/sovereign-veritas/blob/main/CHALLENGE.md);
   anything beyond it needs a written agreement first.
5. **Requests for credentials, access, payment or endorsement** as a condition of contributing, or offers of paid
   services in place of evidence.
6. **Personal attacks or harassment** ([DISCUSSION_NORMS.md](DISCUSSION_NORMS.md)), or publishing anyone's private data.
7. **Promotional spam**, link farming, or a submission that is mainly an advertisement.

Not disqualifying: no degree; using AI with disclosure; disagreeing with the owner; a negative or null result; a wrong
hypothesis honestly tested; English as a second language; slow response.

## 9. Routing: Principia first, any public repo allowed

- The menu lists Principia challenges first, and an OPEN entry with no repository named defaults to Principia.
- Entries for other repositories are welcome. Their evidence record goes in that repository (as vacuity_lint's IE1 did),
  and a one-line pointer is added to `contributions/<handle>/` here, so a contributor's record stays in one place.
- A candidate whose first challenge was elsewhere is invited to Principia for C6 or for their next contribution.
  It is an invitation, not a requirement.

## 10. Privacy, credit and provenance

- Nothing is published without the contributor's written consent. Credit uses their wording, verbatim.
- Private correspondence is summarized at most, never quoted, unless they agree. The owner's own prompts to AI tools are
  never quoted in public records.
- No family, health or personal information about anyone appears in any challenge, issue or record.
- Every record carries the provenance chain: AI participation → human validation → human editing → human responsibility.
  It names the model and only the review level that actually happened.
- Contributors can withdraw at any time. Accepted contributions keep their attribution. A contributor who asks to be
  de-credited is anonymized, but their evidence is not deleted.

## 11. What contributors get, and what they don't

**Participation is free, voluntary, unpaid, and at each person's own pace.** People are welcome to join for fun,
curiosity, learning, or independent scientific inquiry. No membership fees, mandatory hours, assigned workload,
or deadline are imposed.

**The only recognition or non-monetary return offered is accurate attribution and the possibility of having an
accepted contribution published in the relevant repository, with the contributor's informed written consent.**
Credit uses the contributor's chosen wording. Publication depends on evidence review, maintainer acceptance,
licensing permissions, and consent; it is **not guaranteed** for every submission. A reproduced negative result
can qualify just as a positive finding can.

Opportunities to review, undertake blind tests, or apply for tightly scoped repository access are optional
participation paths, **not compensation or entitlements**. No salary, hourly pay, consulting fees, stipends,
expense reimbursement, equity, co-ownership, royalties, profit shares, employment, commercial partnership,
or future financial reward are offered or promised. Co-authorship and write access are not automatic.
Participants need not purchase hardware or services for the project and can stop contributing at any time.

Contributors retain any rights they have in their original work unless separately and expressly licensed or
agreed otherwise; unpaid participation does not transfer intellectual property by itself. If someone wants a
paid or commercial arrangement, it must be negotiated separately **before** such work begins, not assumed
from volunteer participation ([CONTRIBUTOR_TRUST_PATH.md](CONTRIBUTOR_TRUST_PATH.md)).

## 12. Outreach (how candidates are found)

Every substantive reviewer so far arrived through a direct personal channel, not through broadcast posts. So:

- **Direct invitation first.** Send one message to one person, offering one challenge that fits their field and linking
  the menu. Do not mass-message.
- Posts link to the [challenge menu](challenges/entry/README.md), not the repository root.
- Each invitation states the deal plainly: **free, voluntary, unpaid, at your own pace, for learning and
  curiosity**; no required hours or fees; no promised money, equity, ownership or future commercial reward.
  The only offered recognition is proper credit and possible repository publication of accepted, consented work
  (§11). A challenge is an optional trust path, not a prerequisite to independent exploratory research.

## 13. Owner decisions needed before adoption

1. Confirm the public-repository list in the menu (some visibility is unverified).
2. Who runs C3 reproductions besides the owner, and whether an AI re-run is enough for C3 on low-risk items. Under this
   draft it is, but it is labeled as a reproducibility check, never as independent evidence.
3. Seal the first planted-defect and null-answer challenges (§6). None are sealed yet.
4. Whether to link this protocol from README, JOIN_RESEARCH.md and the issue chooser.

*Provenance: drafted by Claude Opus 5.5 (Anthropic) at the owner's direction on 2026-10-18. Human review: none yet.
Responsibility for adoption rests with the owner.*

*Revision (2026-10-18): Owner-directed clarification of voluntary, unpaid participation, recognition,
publication consent, and non-promise of compensation. Drafted with ChatGPT (OpenAI GPT-6); human review level:
owner direction only. Owner retains responsibility.*

*Vincit Omnia Veritas.*
