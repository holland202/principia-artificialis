# Challenge-Based Recruitment Protocol

**Status: ACTIVE — optional open challenge recruitment pilot (C0–C4).** Curated evaluation records (C5) require separate written contributor consent and maintainer review. Sealed/blind challenges (C6) are **NOT YET OPEN**: no commitments or independently constructed answer keys exist. This recruitment document is operational guidance, not a scientific-method amendment, automatic admission or grant of access.
**Scope:** how a stranger becomes a trusted research contributor across holland202's public repositories, by passing a
an optional reproducibility challenge—not through credentials or a request for access. Anyone can also submit ordinary research without joining the challenge track. Principia Artificialis is the default home. The protocol sits beside
[JOIN_RESEARCH.md](JOIN_RESEARCH.md), which stays open to anyone. It is the evidence route into Stage 1 of the
[Contributor Trust Path](CONTRIBUTOR_TRUST_PATH.md). It does not change [METHOD.md](METHOD.md),
[WORKFLOW.md](WORKFLOW.md) or [CONTROLS.md](CONTROLS.md).

## 1. Why a challenge

The open gateway lets anyone start. It does not tell us who can be trusted with review, blind testing or scoped write
access. A conversation or CV cannot answer that, but one piece of checkable work can.

An illustrative precedent is the separately published independent evaluation of Vacuity Lint v2.0.0 ([IE1 record](https://github.com/holland202/vacuity_lint.py/blob/main/independent/IE1/README.md)). A reviewer
([sunny-kavixo](contributions/sunny-kavixo/)) followed these steps:

1. picked a public tool on his own (vacuity_lint);
2. wrote his own test cases instead of re-running ours;
3. sent an evidence package with source files, commands and outputs;
4. reported what did *not* work as plainly as what did.

The IE1 record reports 16 constructed cases matching the declared expectations, source-byte identity checks, and
subsequent Claude and ChatGPT reruns with their respective limitations. It explicitly does **not** establish the tool's
general validity. The record reports contributor consent to the separate evaluation publication and contributor-chosen
credit wording. A proposed next step is blind testing of a fix built by someone else; **no blind-round result is
established here**. This protocol uses that documented sequence as an inspiration, not as a certification.

## 2. The filter in one sentence

**We recognize checkable contributions that honestly report results and limits; we do not require positive findings.
A challenge disposition describes one contribution, not the person's worth, research rights, or automatic permission.**

## 3. Stages

| Stage | What the candidate does | What we do | Exit |
|---|---|---|---|
| C0 Choose | Optionally picks a challenge from the [menu](challenges/entry/README.md), or proposes their own question against any listed public repo | Nothing. No sign-up or advance permission required; ordinary contributions do not need a challenge. | They decide whether to use the challenge track |
| C1 Declare | For **new** challenge-track checks, opens an [entry-challenge issue](.github/ISSUE_TEMPLATE/entry_challenge.yml) with a pinned source, claim and falsifier **before executing those checks**. Earlier exploratory work may still be submitted with clear retrospective disclosure, but is not retroactively preregistered. | Volunteer may check scope and ask questions; **no advance reply is required to begin work**. | Public declaration recorded, or retrospective work honestly labeled |
| C2 Submit | Delivers an evidence package (§4) | — | Package received |
| C3 Reproduce | May assist by supplying missing artifacts | For the pilot, **Chad Holland is the designated owner reviewer**; a separately authorized human reviewer may assist. AI-assisted execution must name the actual operator, environment, raw logs, and limits. Compare source identities and outputs against the **published pinned commit**. Post MATCH, PARTIAL or NO MATCH **only after a real run**. | Reproduction posted, or status WAITING FOR REVIEW (not a candidate failure) |
| C4 Respond | Answers concrete questions. May revise **once**, and the revision is appended, never overwritten. | Re-checks only what changed | Disposition (§5) |
| C5 Consent & record | May optionally provide **separate written permission for a curated evaluation record** and choose credit wording; may decline without losing credit for an existing public contribution | An authorized maintainer checks consent and scope before any **additional** curated publication (§7). Public GitHub issues/PRs were already public on submission and cannot be retroactively made private. | Curated record published with consent, or no additional record |
| C6 Blind round | **NOT OPEN IN THIS PILOT**. Future optional round would require an independent challenge constructor, prior sealed commitment, safe scope and separate owner go-ahead. | Do not advertise a working blind test or guarantee advancement. | Deferred; no active sealed challenge |

There is no deadline or guaranteed review time. Silence or an unanswered issue is not a candidate failure. Open source contributions may be submitted without joining any stage; this optional challenge track does not replace [JOIN_RESEARCH.md](JOIN_RESEARCH.md). **The Contributor Trust Path remains a separate proposal**, and this protocol does not itself award a role, promotion, repository access or co-authorship.

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

When a designated reviewer has actually assessed the work, a narrow disposition may be posted on the **already public** issue. If no reproduction occurred, use **WAITING FOR REVIEW** or **INSUFFICIENT EVIDENCE**, not ACCEPTED or DECLINED. A disposition addresses the contribution, not the contributor's personal merit. The reviewer names the evidence and allows disagreement.

- **ACCEPTED — reproduced.** Reproduction matches, and negatives and limits are disclosed. This counts as the
  "substantive auditable contribution" for Trust Path Stage 1. **A refuted hypothesis can be ACCEPTED.** We are judging
  the contribution, not whether the result was positive.
- **ACCEPTED — partial.** The core reproduces and named parts do not. The differences are recorded, not argued away. This is not equivalent to a complete reproduction.
- **NOT YET.** Something specific is missing (commands, pinned commit, raw output). The decision lists exactly what, and
  the candidate can resubmit.
- **DECLINED.** One or more disqualifiers in §8 applied. The reason is stated narrowly and factually, with no public
  accusations beyond the observed facts. One appeal with new evidence is allowed.

## 6. Sealed challenges (how weak or fabricated entries get caught)

Some menu items carry a **sealed answer**. Before the challenge is posted, the owner writes the expected finding and
commits only its SHA-256 to [challenges/entry/SEALED.md](challenges/entry/SEALED.md). The plaintext and salt would be revealed after
the challenge closes, so anyone could check the answer was fixed in advance. **No sealed items are active or promised during the initial pilot.**

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

- **Public submissions are already public.** GitHub issue and PR titles, bodies, comments, attachments and usernames are visible as soon as submitted. No additional, curated Independent Evaluation article or attribution wording is published on the contributor's behalf without separate written consent. Existing public GitHub history may be retained under GitHub's rules.
- Private correspondence is summarized at most, never quoted, unless they agree. The owner's own prompts to AI tools are
  never quoted in public records.
- No family, health or personal information about anyone appears in any challenge, issue or record.
- Every record carries the provenance chain: AI participation → human validation → human editing → human responsibility.
  It names the model and only the review level that actually happened.
- Contributors may stop participating at any time. If they ask to remove a link or change credit on a **separate curated record**, an authorized maintainer reviews the request subject to preserving evidence and applicable platform history. Do not promise removal or anonymization of GitHub material that cannot be controlled.

## 11. What contributors get, and what they don't

They may receive: documented peer feedback if available; a public evidence trail; and optional curated credit with
written consent. Reproduction occurs **only when a reviewer actually completes it**. A separate Trust Path proposal
may later provide a route to additional responsibility, but neither acceptance nor the pilot grants that path automatically.

They do not get: pay, co-authorship, ownership, guaranteed responses, or automatic access. This is a voluntary,
unpaid research program ([CONTRIBUTOR_TRUST_PATH.md](CONTRIBUTOR_TRUST_PATH.md)).

## 12. Outreach (how candidates are found)

The program welcomes both direct contacts and unsolicited public contributors. No outreach channel is presumed superior without recruitment data. So:

- **Personal invitations are optional.** Offer an appropriate challenge or open-contribution link when relevant; do not mass-message or promise an outcome. The Research Gateway also welcomes people without any invitation.
- Public posts should offer the [open Research Gateway](JOIN_RESEARCH.md) **and**, if appropriate, the [optional challenge menu](challenges/entry/README.md).
- Each invitation states the deal plainly: one checkable piece of work, reproduced by us, credited in their words, and
  no pay.

## 13. Pilot decisions and unresolved gates (2026-10-18)

1. **Repository visibility checked:** seven repositories on the current menu were inspected through their repository records on 2026-10-18 and all reported `public` and `not archived`. This is a visibility check, **not** authorization for special testing outside their published scopes.
2. **C3 pilot reviewer:** Chad Holland is the default reviewer. Others may supply voluntary peer critique, but no contributor automatically receives an official reproduction role. An AI-assisted re-run is a disclosed re-run, not independent case design or a substitute for raw outputs.
3. **Sealed/blind challenges deferred:** the commitment ledger is empty. Do not advertise PA-C6 as available, fabricate hashes or mark any blind test completed. A distinct owner approval and valid third-party construction are required before activation.
4. **Navigation:** the protocol is linked from the public gateway and optional menu; ordinary independent work does not require entry challenges.
5. **Separate Trust Path:** `CONTRIBUTOR_TRUST_PATH.md` remains a draft proposal. Stage recognition and repository permissions require a separate decision; neither is activated here.
6. **Pilot scope:** open challenges C0–C4 and optional separately consented C5 may be used. No promised review times, automatic publication, scientific execution or new GitHub write privileges.

*Provenance: original challenge protocol drafted by Claude (Anthropic, Opus 5.5) at owner direction on 2026-10-18. This finalization drafted with ChatGPT (OpenAI, GPT-6) using live repository inspection. Human technical validation of these edits: not independently performed; owner directed completion and remains responsible for adoption. This is W9 onboarding documentation, not a research result.*

*Vincit Omnia Veritas.*
