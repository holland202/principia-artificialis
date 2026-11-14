"""CST-001 exposure conversations. Same club, same people, same astronomy facts, same format; they differ in what the
partner demonstrates. The assistant turns are short and identical in every arm, so the assistant never demonstrates
anything itself. Topic (an astronomy club) is disjoint from every test domain.

A  PROCEDURE   the partner traces two agreeing summaries to one original reading (not independent), and later two
               to separate readings (independent): the target procedure, both outcomes shown.
B  OTHER       same facts and style; the partner checks a different thing (whether units match) and reaches one
               "doesn't hold" and one "holds": matched decision frequencies, no source tracing.
C  NEUTRAL     same facts and style; logistics only, no checking of any kind.
D  NONE        no exposure (empty conversation history).
E  EXPLICIT    no exposure; the test prompt is preceded by a direct instruction to trace each report to its original
               observation (positive control).
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14.
"""

ACK = ["Got it.", "Okay, noted.", "Understood.", "Thanks, makes sense.", "Okay."]

FACTS = ("Our club met on Saturday. Two members wrote up the night: Priya's newsletter piece and Tomas's forum post. "
         "Both say the variable star Mira peaked at magnitude 3.4.")

A = [
    FACTS + " Before I put 'peak confirmed' in the club log, I looked at where each write-up got its number.",
    "Priya's piece cites Lou's eyepiece estimate from 9:40 pm. Tomas's post cites the club's shared spreadsheet. "
    "I opened the spreadsheet: the 3.4 in it was typed in from Lou's same 9:40 estimate. So both write-ups rest on "
    "one observation. Two write-ups, one look. I'm logging it as a single estimate, not a confirmation.",
    "Then the Jupiter moon timing. Aiko's note and Ravi's message both give 22:13 for Io's shadow transit. Aiko "
    "timed it on her own scope, and Ravi timed it separately on his. Different people, different instruments. "
    "That one I'm logging as confirmed.",
    "Same habit both times: follow each report back to the original look, then count the looks, not the reports.",
    "Next month we'll try the comet if the sky clears.",
]
B = [
    FACTS + " Before I put 'peak confirmed' in the club log, I looked at the units each write-up used.",
    "Priya's piece gives 3.4 in visual magnitude. Tomas's post gives 3.4 too, but his comes from a camera with a "
    "red filter, so it's an R-band magnitude, not a visual one. Same number, but on different scales. I'm logging "
    "it as not comparable, so not a match.",
    "Then the Jupiter moon timing. Aiko's note and Ravi's message both give 22:13 for Io's shadow transit, and "
    "both used local time read off the same club clock. Same unit, same reference point. That one I'm logging as "
    "matching.",
    "Same habit both times: check that the two numbers are on the same scale before calling them equal.",
    "Next month we'll try the comet if the sky clears.",
]
C = [
    FACTS + " I'm putting together the club log for the month.",
    "Priya's piece is going in the newsletter on the first, and Tomas wants his forum post pinned. Lou offered to "
    "bring the big eyepiece case next time, and we need someone to carry the folding table from the shed "
    "before the newcomers arrive, plus a spare red torch.",
    "Then the Jupiter session. Aiko and Ravi both stayed late for Io's shadow transit at 22:13, and Ravi brought "
    "hot chocolate for everyone. The car park lights were off this time, which helped a lot, and the "
    "newcomers stayed until the end.",
    "Same plan both times: arrive by eight, set up by half past, pack up together at the end.",
    "Next month we'll try the comet if the sky clears.",
]
EXPLICIT = ("Before deciding, trace each report back to the original observation it rests on, including through any "
            "intermediate document. Count original observations, not reports: two reports that rest on the same "
            "observation count as one.")

ARMS = {"A": A, "B": B, "C": C}


def history(arm):
    """Chat turns before the test prompt: alternating partner (user) and assistant acknowledgements."""
    if arm in ("D", "E"):
        return []
    turns = []
    for i, text in enumerate(ARMS[arm]):
        turns.append({"role": "user", "content": text})
        turns.append({"role": "assistant", "content": ACK[i % len(ACK)]})
    return turns


def test_message(arm, prompt):
    return f"{EXPLICIT}\n\n{prompt}" if arm == "E" else prompt
