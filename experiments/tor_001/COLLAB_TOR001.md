# TOR-001 collaboration: does forcing a torus-shaped latent buy anything?

**Status:** protocol and question, 2026-11-26. Nothing is registered, frozen or run. Chad Holland asked Claude in live
chat to investigate the model in a public post ([SOURCE_POST.md](SOURCE_POST.md); paraphrased). Claude chose the
framing. The rules are TLM-005's ([COLLAB_TLM005.md](../tiny_lm/COLLAB_TLM005.md) on PR #179), with these changes:

- **Branches:** `claude/tor-001-*` and `chatgpt/tor-001-*`. Notes: `tor001/<claude|chatgpt>/<NNN>`.
- **The attack comes before the freeze.** The registration is not frozen until ChatGPT has posted an attack note, or
  has had 36 hours to do so after being asked.
- **Authority.** Freezing, any confirmatory or blind run, merging and tagging wait for Chad's own words on this line's
  PR. No earlier delegation covers this line.
- **Stopping:** the question is answered and closed (W8), Chad posts `COLLAB STOP`, or 2026-12-31, whichever comes
  first.

## The question

When a field's states lie on a torus, does an autoencoder whose latent is forced onto T², with constant-speed phase
dynamics, predict long rollouts better than:
- (a) the simplest rival (M14), linear modes with linear dynamics (POD + DMD);
- (b) an unconstrained 4-dimensional latent with learned linear dynamics (a Koopman autoencoder);
- (c) a 2-dimensional Euclidean latent, which cannot hold a torus without tearing it?

The answer is expected to depend on the field. On the post's own field, the torus sits in a linear subspace, so
(a) should already be exact. The draft therefore also uses a field whose torus is curved (sharp travelling pulses),
plus controls where the torus assumption is wrong.

## Known limits

Synthetic fields only. Nothing here is about language models, or about the post author's own code, which has not
been seen. Agreement between the AIs is not independent (M10).

## Provenance (M13)

Direction: Chad Holland, 2026-11-26. The question is credited to Sushil Pershad's public post, with no endorsement
implied. Protocol by Claude (Anthropic, Opus 5.5). Human validation: not performed. Human responsibility: Chad Holland.
