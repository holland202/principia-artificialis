# CCC-001 matched pairs: intake of Gemini's Set 1, and a deviation

**Status:** intake record (C-EXT). Nothing was run on a model. The brief is
[PAIRS_AUTHOR_BRIEF.md](PAIRS_AUTHOR_BRIEF.md) at `0a34d88`. Set 1 is kept verbatim at
[`docs/external/ccc001_pairs_gemini_set1_2026-11-23.txt`](../../docs/external/ccc001_pairs_gemini_set1_2026-11-23.txt)
(`1cefacd`, SHA-256 `f347251a02baef856507d33941fa7e1b2886f7d922a907d3c6140552dcd033ce`).

## Deviations, first

1. **Set 2 is not sealed from Claude.** Chad Holland pasted Gemini's whole reply, Set 2 included, into a live chat
   with Claude on 2026-11-23. The brief said Set 2 stays with Chad and only its hash is committed. Set 2 is not
   committed and Claude has not checked it. SHA-256 of the full reply as Claude transcribed it (the line `Gemini`,
   then Set 1 and Set 2, one item per line, trailing newline):
   `618b11ab6c58a5d174d4bfab59aa9360bdff33e9537d10245389d1ea4a0966b7`. Whether Set 2 is retired or kept and labelled
   "seen by Claude" is Chad Holland's decision. It has not been shown to ChatGPT through the repository.
2. **No model version.** The brief asked for the exact model name and version on the first line. The reply says
   only `Gemini`.
3. **Independence is CONTRIBUTOR REPORTED.** Gemini has worked on Principia before (`docs/GEMINI-ATW-001_*`).
   Whether this session had memory, history or repository access is not recorded here.

## Counts (SELF-TESTED, Python on the committed file)

```
items 24 pairs 12
types Counter({'AB': 4, 'AC': 4, 'BC': 4}) keys Counter({'A': 8, 'B': 8, 'C': 8})
first-listed key {'A': 4, 'B': 4, 'C': 4}
```

Every pair shares its claim and has the two keys its type names. Words changed between the two reports, per pair
01–12: `9 1 4 1 3 12 11 4 8 6 5 11`.

## Defects found on reading (Claude's reading, not the human look C-SYNTH asks for)

- **Pair 02: keys inverted.** The claim is "departed after 7:15". The item keyed B says 7:20, which makes the claim
  true. The item keyed A says 7:10, which makes it false. Checked by arithmetic.
- **Pair 07: unit missing.** "twenty-six degrees" is below freezing only in Fahrenheit. The A key depends on it.
- **Borderline keys:** pair 05's C item lists only weekday hours, which some readers will take as evidence against
  Sunday opening (B). Pair 03's B item rests on "refilled the basin for the weekend", which suggests but does not
  state that the fountain is running.
- **Possible surface cue:** in pairs 06, 07 and 12 the C report changes the object being described (11–12 words
  changed). A reader could find C from low word overlap with the claim. Pairs 02 and 04 change one word. Rule 7 of
  the brief asked for no cue of this kind. Not measured on a model.

## Open

- Chad Holland reads a named sample of pairs himself (C-SYNTH) and decides on Set 2.
- Pairs 02, 03, 05 and 07 are kept verbatim. Any corrected version is a separate file that names what changed.
- Nothing is registered: no endpoint, threshold or prediction uses these items yet.

## Provenance (M13)

Items: Gemini (Google), version not stated, 2026-11-23, relayed by Chad Holland. Intake, counts and reading:
Claude (Anthropic, Opus 5.5). Human validation: not performed. Human responsibility: Chad Holland. The question
behind CCC-001 is Federico Talens-Alesson's. Crediting him implies no endorsement or validation by him.

## Changes (W9)

- **2026-11-23, later:** Set 2 replaced. Chad Holland asked a new Gemini chat, with memory off (CONTRIBUTOR
  REPORTED), for a new Set 2, saved it on his device and sent Claude only this line from Termux:
  `370439216199e9350e16555b4d0e3a8787831dff834f7900722063d8ac324275  /data/data/com.termux/files/home/set2_v2.txt`.
  Claude has not seen that file. Its contents, its pair count and the Gemini version that wrote it are not checked
  here. The first Set 2 (hash `618b11ab…`, seen by Claude) is retired from held-out use, following Chad Holland's
  choice in a live chat (paraphrased). Deviation 1 above stays as written. Appended by Claude (Anthropic, Opus 5.5);
  human responsibility: Chad Holland.
- **2026-11-23T02:38–02:39Z:** Chad Holland recorded the choice of Gemini as author on PR #172 in his own words
  ([comment 7090094126](https://github.com/holland202/principia-artificialis/pull/172#issuecomment-7090094126)), with
  the replacement Set 2 hash above. He gave the model version as "Gemini 4 Hydrogen"
  ([comment 7090106532](https://github.com/holland202/principia-artificialis/pull/172#issuecomment-7090106532)),
  CONTRIBUTOR REPORTED. The provenance line above ("version not stated") describes Gemini's own reply and stays.
  Appended by Claude (Anthropic, Opus 5.5); human responsibility: Chad Holland.
- **2026-11-23, corrected copy:** at Chad Holland's direction in a live chat (paraphrased), Claude wrote
  [`pairs_set1_corrected.txt`](pairs_set1_corrected.txt) (SHA-256
  `0332c40c65f25006ede386b804fe8af5ccd83570ce2f3ce3d9ad2e2af716f921`). The verbatim file is unchanged. Every change:
  - First line: `Gemini` became `Gemini (Set 1, corrected by Claude; see PAIRS_SET1_INTAKE.md)`.
  - Pair 02: keys swapped (7:20 is now A, 7:10 is now B). Report text unchanged.
  - Pair 03, item B: "refilled the basin for the weekend" became "refilled the basin to keep it running all winter".
  - Pair 05, item C: "; its weekend hours are posted only on the store's website" added after "eight until six".
  - Pair 07, item A: "twenty-six degrees" became "twenty-six degrees Fahrenheit".
  The three reworded reports (03 B, 05 C, 07 A) are now **Claude-edited**, not Gemini's alone. Results on them are
  labelled that way. The possible word-overlap cue (pairs 06, 07, 12) was not rewritten. A word-overlap rival is
  proposed for the pilot instead (M14). Counts after correction: 24 items, A 8, B 8, C 8, longest report 25 words.
- **2026-11-23T02:55Z, human look (C-SYNTH):** Chad Holland read pairs 01, 02, 03, 05, 07 and 10 of the corrected
  copy (`ac5f1e2`) and agreed with their keys, in his own words on PR #177
  ([comment 7090321905](https://github.com/holland202/principia-artificialis/pull/177#issuecomment-7090321905)).
  Pairs 04, 06, 08, 09, 11 and 12 were not read by a person. Appended by Claude (Anthropic, Opus 5.5); human
  responsibility: Chad Holland.
- **2026-11-24, replacement Set 2 exposed to Claude.** In a live chat at about 19:15Z, Chad Holland pasted to Claude
  a 48-item list headed `Gemini` with pairs numbered `2 | 01` to `2 | 24`, and asked Claude to file it. Claude
  presumes this is the replacement Set 2 but could not confirm it. The SHA-256 of Claude's transcription (with and
  without the header line and trailing newline) does not equal the committed hash `37043921…`. The closest form,
  the transcription as pasted with a trailing newline, hashes to
  `199d92c9770d260a086ca54c9572e277d28039d7db20e342ca1d13096500e910`; the difference is probably in bytes a paste
  does not carry. **The text is not committed, and Claude deleted its working copy after hashing.** Claude has
  not scored, analysed or discussed the items. Whatever it is, the replacement Set 2 must now be treated as seen by
  Claude, like the first. Before any confirmatory use, a fresh held-out set is needed, written by an author outside
  the relay and shown to neither AI. That set lives only with Chad Holland: not on GitHub and not pasted into any AI
  chat. Appended by Claude (Anthropic, Opus 5.5); human responsibility: Chad Holland.
