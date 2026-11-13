# Intake note — 2026-11-13: "Growth and Decay in AI Memory"

This is reference material, not a research note. It registers no predictions, has no reference code, and adds
nothing to NOTES_INDEX.md. It records a supplied research synthesis, checks a subset of its claims against their
primary sources, and lists questions that could be tested. Nothing here was run or reproduced.

**Disposition:** registered as an external synthesis (C-EXT). It is useful as a map of the literature. It is
**not** independent evidence for any of its conclusions. Its central engineering recommendation is untested in
the sources it cites: decay should be "reversible rank demotion" rather than "destructive TTL/LRU deletion." That
gap is the question proposed as MEM-DECAY-001, which is filed separately.

## What failed or did not hold (read first, M8)

Eight primary sources were checked on 2026-11-13. Two held as stated (listed after this list). The other six need a
correction or a caveat. Each item names the source it was checked against.

1. **An undisclosed author interest in the forgetting benchmark.** ForgetEval ("Control-Plane Placement Shapes
   Forgetting", arXiv:2606.15903v2) has one author, Dongxu Yang, listed with the affiliation DeepLethe. The paper
   treats Lethe as its own reference implementation. The document presents Lethe's and Lethe+LLM's scores
   (63.4%, 91.7%) with no note of this interest. The scores themselves match Table 2 of the paper:
   - Lethe 244/385;
   - Lethe+LLM 353/385;
   - Mem0 (infer=False) 263/385;
   - LangMem 242/385;
   - MemPalace 0/385;
   - compound-fact supersession 0/40 for each deterministic system and 31/40 for Lethe+LLM.
2. **FadeMem does not compare against TTL, LRU or no decay** (arXiv:2601.18642v1).
   - Its baselines are fixed context windows with FIFO eviction, LangChain memory, Mem0 and MemGPT.
   - It does not say whether pruned memories can be restored.
   - Its 85.9% factual consistency is measured on LoCoMo, not on LTI-Bench as the document says. The 68.9%
     conflict-resolution figure is the LTI-Bench macro average (contradiction 66.2%, update 87.1%, overlap 53.4%).
3. **DMF has no decay ablation** (arXiv:2606.03463v1). It is compared only against Mem0, with no no-decay and no
   TTL/LRU control. Its half-life arithmetic checks out: ln 2 / 0.035 = 19.80 turns at Ω = 0 and 39.6 turns at
   Ω = 1. Evicted entries are archived as raw records, not deleted.
4. **Attention-mass study** ("Length Is Cheap, Competition Is Not", arXiv:2611.04169v1). The 126,473 trials and
   the R² ranges (0.35–0.58 for log(1/a*), 0.02–0.08 for log length) match. Three things do not:
   - The ranges come from short contexts (L ∈ {512, 1024, 2048}) on five open models of 0.5B–3B parameters. The
     document places them at "8K–32K".
   - The "tolerates about half the evidence attention, then fails" threshold is reported for Qwen2.5-1.5B only.
   - The paper says it reports "no universal law." The document's design rule built on that threshold
     ("super-linear accuracy loss emerges once evidence attention mass drops roughly in half") generalises past the
     source.
5. **Continual fact learning** (O'Neill, arXiv:2607.11020v2). The 27.4 → 5.4 gap, 1% vs 46% after 20 writes, the
   +37.6-point effect (95% CI [28.9, 46.3]), the 69%/79% (57%/67% drift-corrected) retained lift, and Spearman
   ρ = 0.83 / 0.946 all match. Three framings do not:
   - The main experiments use Qwen3-4B. Qwen3-8B replicates only the entailment gap, not "4B and 8B models"
     throughout.
   - "68.8%" does not appear; "70%" does.
   - The +37.6 effect compares study-style with bare-statement later writes.
6. **MemoryAgentBench** (arXiv:2507.05257v4). The FactConsolidation figures match Table 3:
   - GPT-5-mini 78.0 / 28.0 (avg 53.0);
   - HippoRAG-v2 54.0 / 5.0 (29.5);
   - BM25 48.0 / 3.0 (25.5);
   - Mem0 18.0 / 2.0 (10.0);
   - multi-hop by length: o4-mini 80.0 → 14.0, GPT-4o 28.0 → 10.0 (6K → 32K).

   Two things do not:
   - The arXiv page states no venue, so the document's "ICLR 2026" is not confirmed.
   - Its "262K-token selective forgetting" label was not found on the table.

Two vendor-gap and practitioner claims are weaker than the document presents them:

- **Mem0 LongMemEval gap.** The comparison page cited (Digital Applied) gives Mem0's own 94.4 against
  "49.0 — Vectorize's own evaluation, March 15, 2026." Vectorize is a competitor, and the page does not name the
  judge model. The document's "93.4" and "Zep 66.88–68.44%" are not on that page (they were not checked elsewhere).
- **"Automated decay is disabled by default across major platforms."** This comes from The Agent Field Guide, an
  unsigned page dated 2026-09-02. It states this without citation and names no platforms. The same page cautions
  that "no study yet isolates decay-based pruning against retrieval precision on a shared benchmark." The
  document's TTL/LRU "allergies or compliance rules" example is not on that page; its stated source (a Krish Naik
  tutorial, works-cited #14) was not checked.

Held as stated: **lifecycle cost** ("Agent Memory: Characterization and System Implications", arXiv:2606.06448v2).
All eight figures match:

- construction energy 32 J (BM25), 99 kJ (HippoRAG v2) and 1,050 kJ (Mem0);
- Table 3: BM25 47.0% / 16.3 min / 582 kJ; HippoRAG v2 44.3% / 44.2 min / 1,339 kJ; Mem0 32.0% / 4.02 h / 4,878 kJ;
  Letta 27.7% / 14.36 h / 15,429 kJ.

Scope the document leaves out: the construction figures are for one LongMemEval sample. Table 3 covers five samples
and 300 queries on Qwen3-32B, run on one H100.

Held as stated: **revocation enforcement** ("Revoked but Still Authoritative", arXiv:2609.08258v1, Shen, Toyoda and
Leung):

- Graphiti returns the revoked record and its status by default. Zep CE returns it but never returns the status flag.
- mem0 filters it at read time by default, but returns it under an expiry-flag override ("one boolean in a shipped
  product"). langmem and cognee keep no revoked record by default.
- Graphiti and mem0 (exp.) returned the revoked fact in 81/81 cells, ranked above its replacement.
- Unsafe-action rate pooled: 699/1,620 (43.1%). Prompt hardening alone brought it to 37.2%. A store-level filter
  brought it to 0/1,620.
- The guard's own measured results (§5) were not read.

## The supplied document

| | |
|---|---|
| File | [`docs/external/ai_memory_growth_and_decay_2026-11-13.pdf`](../docs/external/ai_memory_growth_and_decay_2026-11-13.pdf), byte-identical to the file supplied |
| SHA-256 | `2a3d7268f775af98aa912a87e573210d6c04da3651c7a43ff688e8890f5d3811` |
| Form | 15 pages, PDF title "AI Memory Growth and Decay", exported by the Google Docs renderer; 85 works cited |
| Author / tool | Not stated in the file. Supplied by Chad Holland on 2026-11-13. ChatGPT reviewed it first, at his request; that review is not reproduced here |
| Visible defects | Leftover generator markers in the text (`[span_93](start_span)…`, `[span_7]`, `[span_264]`, `[span_286]`, `[span_288]`, `[span_297]`) |

## Evidence classes

Classification follows how each source presents itself. **Checked** means it was read against its primary page
on 2026-11-13. **Unchecked** means the class is taken from the document's own citation.

| Class | Sources (works-cited number) | Status |
|---|---|---|
| **Peer-reviewed, as cited** | Nanda et al. 2023 grokking (#10); Liu et al. NeurIPS 2022 (#35); Chu et al. ICML 2025 (#39–41); Biderman et al. TMLR 2024 (#45–47); SimNPO NeurIPS 2025 (#52); quantization unlearning ICLR 2025 (#49, #55); Jelassi et al. ICML 2024 (#67); Titans NeurIPS 2025 (#68); MIRAS ICLR 2026 (#11); KV pseudo-query EMNLP 2025 (#3); Mamba recall EMNLP Findings 2026 (#4); Dohare et al. Nature 2024 (named in the text, no works-cited entry) | Unchecked: venues as the document states them |
| **Preprints, checked** | 2609.08258 (#16), 2606.15903 (#80), 2507.05257 (#82), 2601.18642 (#13), 2606.03463 (#78), 2607.11020 (#5, #37), 2611.04169 (#7), 2606.06448 (#77) | Checked; findings above |
| **Preprints, unchecked** | Survey 2512.13564 (#1, #22); 2609.10657 grokking scaling (#31); 2609.33334 DGE (#12, #63); 2606.00382 CRMA (#48); 2509.04259 RL's Razor (#42–44); 2611.05866 (#54); 2610.05872 (#24); 2601.07978 (#18); 2609.32341 (#65); 2507.06457 (#66); 2501.09166 (#72); 2602.02139 (#51); 2504.06407 (#56) | Unchecked |
| **OpenReview submissions / reviews** | #15, #25 (Morris et al., memorization capacity), #26, #44, #53, #62, #63, #73, #75 | Unchecked; review comments are not findings |
| **Vendor-reported** | Mem0 scores (via #17, #19, #20); Zep/Graphiti scores; Chroma context-rot study (via #6, #28, #58, #60); Samsung LookaheadKV (#57); Atlan "73% of RAG failures" (#76); Onyx (#30); Cognee guides (#21, #81) | Vendor claims; the gap figure above was checked |
| **Third-party or competitor evaluations** | Vectorize 49.0 on Mem0 (via #17, checked); Dakera (#19); René Zander (#20); innernet labs (#83) | Competitor interest likely; only #17 checked |
| **Unverified, practitioner or secondary** | llm-stats "25–30% working ceiling" (#27); Towards AI HR example (#9); Pickaxe (#8); Krish Naik (#14); Agent Field Guide (#79, checked); independent preprint on λ_c (#23); Reddit (#74); Emergent Mind / nnsight / AI Engineer / TestMu / diffray / OvalEdge / Medium / Oracle / GitHub design note (#29, #32–34, #36, #43, #58–60, #84, #85) | Not evidence for quantitative claims |
| **Mirrors or secondary copies of works above** | #2, #38, #40, #46, #47, #50, #61, #64, #69–71 | Not separately classified |

## Prior art for the decay question (found 2026-11-13, before proposing anything as new)

- **MaRS / FiFA** ("Forgetful but Faithful", arXiv:2512.12856, Alqithami, preprint 2025-12-14). This is the closest
  prior work. It compares six forgetting policies, including FIFO, LRU and Priority Decay, under memory budgets.
  It reports Priority Decay ahead of the temporal baselines on narrative coherence (0.604 ± 0.062 vs. FIFO 0.529,
  LRU 0.501). It also argues that LRU is near-optimal when usefulness decays exponentially with age. The policy
  names and figures come from the PDF text; the abstract page names only the hybrid policy. Whether its evictions
  are reversible was not established.
- **AMV-L** (arXiv:2603.04443). Compares TTL, LRU and its own lifecycle policy for tail latency. It reports that TTL
  leaves the eligible retrieval pool unbounded and that LRU is value-agnostic.
- **Mem0's own guidance page** (vendor). It recommends TTL for retention obligations, LRU-style decay on retrieval
  scores, and a "salience floor" so high-importance facts cannot be pruned on time alone. It describes its decay as
  down-ranking, not deletion.
- **MemDecay** (arXiv:2607.10582). Covers KV-cache eviction, not stores. Pinning kept system-region facts where no
  baseline kept more than 13 of 24.

None of these, as read, runs **no decay vs. destructive TTL/LRU vs. reversible rank decay** on one frozen set with
critical constraints, revoked records and adversarial retrieval together. That combination is the open question.
It is not a claim that the idea is new.

## Falsifiable questions (candidates, none registered)

Each is stated so it can be wrong. Each needs an anti-vacuity control before registration (M3).

| ID | Question | What would refute it | Feasible locally? |
|---|---|---|---|
| Q1 growth | At a fixed query set, does retrieval precision@k fall as distractor records grow 10×? | No fall beyond the same-input noise band (C-NOISE) | Yes, with a fixed embedding |
| Q2 neighbourhood | Do distractors that share vocabulary with the target lower precision more than an equal number of unrelated distractors? | The two arms equal within noise | Yes |
| Q3 supersession | Without supersession links, is the stale value ranked above the current one when the stale record is closer to the query? | Current value ranked first in every case | Yes |
| Q4 reversible decay | Does rank-only decay suppress stale records as well as TTL/LRU while losing zero critical constraints? | Rank decay loses a critical item, or suppresses stale items worse than TTL/LRU | Yes (MEM-DECAY-001) |
| Q5 revocation | Without a retrieval-time guard, is a soft-revoked record returned? With one, is it returned 0 times? | Guarded store returns a revoked record; unguarded store never does (then the test cannot discriminate) | Yes |
| Q6 access vs storage | Does a "forgotten" fact keep most of its log-probability lift after sequential fine-tuning? | Lift returns to the pre-write floor | No: needs fine-tuning on a GPU |

## Possible applications to SML (no change made, no experiment started)

SML (public, `holland202/sovereign-memory-layer` at
[`6262dbe`](https://github.com/holland202/sovereign-memory-layer/tree/6262dbe362c77e2cf8ecf9c326517c494dc125e8))
already has three of the mechanisms the document discusses. Read from `sml/memory.py`:

- **Retrieval-time revocation guard.** `_retrieve_from` skips every record whose status is not `current`, so
  `revoked` and `superseded` records are never returned by `retrieve()`. This is the store-level filter that took
  unsafe actions to 0/1,620 in 2609.08258. SML has not yet been tested against that paper's scenarios (Q5).
- **Reversible rank decay.** `method="recency"` and `"importance"` multiply the score by
  `exp(-ln 2 · age / half_life)` (default 30 days). They delete nothing.
- **Destructive pruning.** `compact()` removes whole unprotected correction chains by lowest weight. `protected`
  chains are never removed. If protection blocks the target, the call fails and nothing is committed. This is
  importance pruning, not TTL or LRU; SML has no TTL or LRU arm.
- Known limit already in SML's README: it is "not shown to retrieve better than most recent first."
  `hash_embedding` is a lexical hash, so Q1–Q2 would need supplied embeddings to say anything about semantic
  neighbourhoods.

Applications to the owner's private integration workspace are not recorded here. It is private, and this repo is
public.

## Provenance (M13)

ChatGPT (OpenAI) reviewed the supplied document first, at Chad Holland's request. Claude (Anthropic, Opus 5.5) then:

- hashed and preserved the document;
- checked eight primary sources plus two secondary pages against it;
- searched for prior art;
- read SML at the pinned commit;
- drafted this note.

The checks were made through a fetch tool that summarises pages, so the quoted figures should be spot-checked
against the PDFs before anyone builds on them. Human validation: not performed. Human editing and curation:
direction by Chad Holland. Human responsibility: Chad Holland. Review level: direction only.
