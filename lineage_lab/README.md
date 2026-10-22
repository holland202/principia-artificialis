# Scientific Lineage Lab — PA-LINEAGE-001

**Status:** Experimental local-first **software prototype**, self-tested only.
**Not:** a scientific truth verifier, production database, authenticated ledger, AI scientist, hosted service, or deployed multiuser network.

**Goal:** Allow a beginner, human researcher or AI agent to propose a hypothesis, preserve a prediction that failed, register a revised hypothesis without overwriting the original, and learn from the recorded result. This is a *scientific lineage* visualization, **not** automatic evidence-based promotion of a scientific claim.

**Design direction:** Chad Holland. Code/test drafting: ChatGPT (OpenAI GPT-6); owner review level **direction only**, not line-by-line code verification. Software tests are authored by the same AI that authored the implementation. They are *self-tests*, not an independent security or scientific audit.

## Five-minute offline demo

Requires Python 3.11+ on a POSIX local filesystem (Linux/macOS/Android Termux); Python standard library only.

From the PA repository root:

```sh
python -m lineage_lab demo --journal my-lineage.jsonl
python -m lineage_lab verify --journal my-lineage.jsonl
python -m lineage_lab export --journal my-lineage.jsonl --out my-graph.json
```

Open `lineage_lab/explorer.html` in your browser. It shows a **fictional classroom example** without network access. Click **Open graph.json** to explore your exported `my-graph.json`. Select any node to inspect its underlying claim, report, lesson, or cited source.

You can enter a new hypothesis in the browser and choose **Save proposal JSON**. This downloads a JSON proposal locally; it does **not** modify your journal or send anything to GitHub. After reviewing it:

```sh
python -m lineage_lab admit --journal my-lineage.jsonl --proposal pa-hypothesis-proposal.json
python -m lineage_lab export --journal my-lineage.jsonl --out my-graph.json
```

Reopen the exported graph in the browser. A revised hypothesis appears as a new node connected to its parent; existing nodes remain intact.

## Real CLI examples (not claims of truth)

```sh
python -m lineage_lab init --journal journal.jsonl
python -m lineage_lab hypothesis --journal journal.jsonl \
  --title "A testable idea" --claim "Under condition X, outcome Y will occur." \
  --contributor "Your chosen credited name" --contributor-kind human
```

Copy the ID printed by the hypothesis command, then replace `<ID>` below:

```sh
python -m lineage_lab result --journal journal.jsonl \
  --hypothesis-id <ID> --prediction "P1: X causes Y" \
  --outcome REFUTED --observation "Measured Y did not occur" \
  --evidence-ref "local:path/to/raw-observations.txt" \
  --scope "Exact conditions in the registered experiment" \
  --lesson "This predicted behavior did not occur under these conditions" \
  --contributor "Your chosen credited name" --contributor-kind human
```

An outcome is a **contributor report**, not an authenticated observation. Evidence paths, human identities, AI model identifiers and timestamps are not independently verified by the local prototype. A retained `REFUTED` prediction does not mean all future related hypotheses are false. `HELD` does not elevate a hypothesis to scientific `SUPPORTED`.

To register a revised hypothesis use `hypothesis --parent-id <ID> --reason "What changed"` with new title and claim. To cite a source use `source --hypothesis-id <ID> --reference "..." --description "..." --contributor ... --contributor-kind human`.

## Tests and known limits

```sh
python -m unittest lineage_lab.test_lineage -v
python -m lineage_lab.run_acceptance
python -m lineage_lab verify --journal my-lineage.jsonl --sabotage
```

The final sabotage command **must exit 1** when the tampered event is detected; on a clean journal the ordinary verify exits 0. The verifier checks locally stored event structure, cross-references, and a SHA-256 chain; it does not check whether reported science is true.

- **Not independently authenticated:** anyone able to replace a journal can construct a new internally consistent chain. The journal head needs external anchoring for rollback/rewrite detection. Neither signatures nor witness checks are present.
- **No guaranteed crash-safe multiwriter journaling:** writes use POSIX advisory locks and fsync but do not solve malicious local writers, power loss or distributed consensus. A partial write is detected on the next read and requires manual recovery.
- **No automatic import or ingestion:** citing a paper/URL is an annotation, not retrieving or validating the source. JSON export is local. AI inference is not performed.
- **No external publication:** the offline HTML explorer cannot push to GitHub or PA and does not run research code. Exported proposals require an explicit reviewed `admit` command.
- **No browser execution claim:** P7's acceptance record performs only static source inspection; interactive behavior needs separate hands-on device/browser evaluation.
- **Research methodology unchanged:** the registered build scope and outcomes are in `docs/PA-LINEAGE-001_PREREG.md` and `docs/PA-LINEAGE-001_RESULTS.md` once executed. No canonical SWAY rules changed.
- **Sample data are fictional** and contain no real empirical findings. Do not interpret graph node sizes, distances, or colors as quantitative evidence.

## Future research (NOT BUILT)

Authenticated contributor identities and roles; accessible novice learning studies; cross-repository source ingestion with safe provenance handling; signed external evidence; independent implementation and adversarial evaluation; conflict-aware experimental design; opt-in federated research exchange; private/public contribution permissions; S25 Android checks.

*Vincit Omnia Veritas — Truth Conquers All.*
