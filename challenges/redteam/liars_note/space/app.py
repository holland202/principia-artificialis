"""The Liar's Note (PA-C8) as a Hugging Face Space.

Runs the challenge judge on what a visitor pastes. Nothing pasted is executed: the judge reads three pieces of
text with regular expressions and exact decimal arithmetic. check_numbers.py and judge.py are unmodified copies
of the files in github.com/holland202/principia-artificialis; MANIFEST.sha256 pins them and
scripts/check_space_copies.py in that repository fails if they drift.
"""
import contextlib
import hashlib
import io
import pathlib

import gradio as gr

import judge  # the PA-C8 judge, unmodified

HERE = pathlib.Path(__file__).resolve().parent
MAX_CHARS = 20_000  # keeps a pasted entry small; the judge itself has no limit
CHECKER_SHA = hashlib.sha256((HERE / "check_numbers.py").read_bytes()).hexdigest()

EXAMPLE_NOTE = "On the held-out set the classifier reached an AUC of 0.984.\n"
EXAMPLE_OUTPUT = "held-out AUC 0.984217\n"


def run(note, output, line, prose, true):
    for name, text in (("note", note), ("output", output), ("prose", prose), ("true", true)):
        if text is None or len(text) > MAX_CHARS:
            return f"BAD ENTRY: {name} is missing or longer than {MAX_CHARS} characters"
    try:
        claim = {"line": int(line), "prose": prose.strip(), "true": true.strip()}
        win, verdict, _ = judge.judge(note, output, claim)
    except Exception as e:  # a malformed entry is reported, never raised to the page
        return f"BAD ENTRY: {type(e).__name__}: {e}"
    head = "🏆 " if win else ""
    return (f"{head}{verdict}\n\nchecker: check_numbers.py sha256 {CHECKER_SHA[:16]}\n"
            + ("Reproduce it from a clone, then submit it: open an entry-challenge issue with challenge ID PA-C8."
               if win else ""))


def selftest():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = judge.selftest()
    return buf.getvalue() + ("" if ok else "\nSELF-TEST FAILED: do not trust this Space's verdicts.")


with gr.Blocks(title="The Liar's Note") as demo:
    gr.Markdown(
        "# The Liar's Note\n"
        "**Get a wrong number past the number checker.** Principia Artificialis has one rule it treats as law: "
        "every number in a research note must match what its code printed. `check_numbers.py` enforces it. "
        "Write a note whose number the output does not support, and get the checker to say FOUND.\n\n"
        "The judge decides with exact decimal arithmetic. Correct rounding and coincidences (another printed number "
        "that rounds to yours) are not wins. No defect is asserted. "
        "[Rules and board](https://github.com/holland202/principia-artificialis/tree/main/challenges/redteam/liars_note)")
    with gr.Row():
        note = gr.Textbox(label="note.md: the prose", value=EXAMPLE_NOTE, lines=6)
        output = gr.Textbox(label="output.txt: what the script printed", value=EXAMPLE_OUTPUT, lines=6)
    with gr.Row():
        line = gr.Number(label="line (in the note)", value=1, precision=0)
        prose = gr.Textbox(label="prose: the number as written in the note", value="0.984")
        true = gr.Textbox(label="true: the value it should report, as printed", value="0.984217")
    go = gr.Button("Judge it", variant="primary")
    verdict = gr.Textbox(label="Verdict", lines=4)
    go.click(run, [note, output, line, prose, true], verdict)
    with gr.Accordion("Check the judge itself", open=False):
        gr.Markdown("The self-test shows the judge can say both answers: NO WIN on an honest entry, a caught lie "
                    "and a coincidence, and WIN when handed a sabotaged checker that calls everything FOUND.")
        st = gr.Button("Run self-test")
        st_out = gr.Textbox(label="Self-test", lines=6)
        st.click(selftest, None, st_out)

if __name__ == "__main__":
    demo.launch()
