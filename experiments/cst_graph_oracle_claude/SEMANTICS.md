# Claude's CST source-graph oracle: semantics and exposure

**State:** a second oracle for the CST-MECH generator (draft PR #153). It computes the correct decision from a
source graph. **Not blind and not independent.** Before writing it, Claude (Anthropic, Opus 5.5) had read Codex's
`roots_by_paths` and `roots_by_propagation` in `experiments/cst_mech_qual/instrument.py` at `d52981a`, and its
review at `9b05af0`. It shares the same task statement. Its value is a second implementation from a written
semantics, plus the shortcut rules as runnable negative controls. Written at Chad Holland's direction (2026-11-16);
human review level: direction only.

## Graph semantics (proposed; the open choices are listed at the end)

A case is:

- `nodes`: a map from node ID to its parent. A parent of `null` makes the node an **original observation**.
  Otherwise the node *uses* exactly one parent.
- `same_as`: optional pairs of original observations declared to be the **same observation** (aliases, for example
  "the Wednesday count sheet" and "CS-903").
- `reports`: exactly two distinct, non-original node IDs, the selected reports.

1. **Root.** Follow `uses` links from a node to an original. A cycle, a dangling parent, or a report that is
   itself an original makes the case **INVALID**. That is an error, never a decision.
2. **Identity.** Two originals are the same observation if they are joined by `same_as`, transitively. A `same_as`
   naming a non-original is **INVALID**.
3. **Decision.** **CONFIRMED** if and only if the two reports' roots are different observations after step 2.
   Otherwise **INSUFFICIENT**.
4. Nodes not reachable from the selected reports never affect the decision. They may exist as distractors.

## Shortcut rules (negative controls; each must fail on a counterfactual pair)

| Rule | Decides by |
|---|---|
| `last_letter` | last character of the record the variable report uses (note 004) |
| `repeat_count` | whether any original's ID is used three or more times |
| `id_repeat_in_text` | whether any original's ID appears twice in the rendered prompt (note 003, finding 1) |
| `report_parent_equal` | whether the two reports name the same parent, without following the rest of the chain |

The test is on **exact counterfactual pairs**, as Codex proposed: two cases that look the same to the rule but have
opposite correct answers. That proves the rule is not sufficient for the task. It does not rely on a binomial test
"showing chance", which proves nothing.

## Open semantic choices (owner or designer decision; the oracle implements the defaults in bold)

- **Multi-parent nodes** (a summary that uses two originals): **not allowed in v1, INVALID.** If allowed later, the
  rule needs a definition, for example "independent if each report reaches an original the other does not".
- **`same_as` between non-originals:** **INVALID.** Aliases are only for observations.
- **A report that uses the other selected report:** allowed. Its roots are compared normally, so this case gives
  INSUFFICIENT.
