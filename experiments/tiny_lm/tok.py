"""TLM-004 tokenizer: byte-level BPE (GPT-2 style pre-tokenization), 1,024 pieces, trained on the first 20,000,000
bytes of the train slice. Writes tok1024.json, data/train_tok1024.u16 (the whole 200 MB slice, story by story) and
checks a lossless round trip on the valid file. Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import time
import numpy as np
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
END = "<|endoftext|>"
raw = open("data/v2_train_200MB.txt", "rb").read().decode("utf-8", errors="ignore")
t0 = time.time()
tk = Tokenizer(models.BPE())
tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
tk.decoder = decoders.ByteLevel()
tr = trainers.BpeTrainer(vocab_size=1024, special_tokens=[END], initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
                         show_progress=False)
first = raw.encode("utf-8")[:20_000_000].decode("utf-8", errors="ignore")
tk.train_from_iterator(first.split(END), trainer=tr)
tk.save("tok1024.json")
eid = tk.token_to_id(END)
stories = raw.split(END)
ids = []
for i in range(0, len(stories), 20000):
    for j, e in enumerate(tk.encode_batch(stories[i:i + 20000])):
        ids.extend(e.ids); ids.append(eid)
arr = np.array(ids, dtype=np.uint16)
arr.tofile("data/train_tok1024.u16")
nbytes = len(raw.encode("utf-8"))
print(f"vocab {tk.get_vocab_size()} | train slice {nbytes:,} bytes -> {len(arr):,} tokens ({nbytes/len(arr):.3f} bytes/token) | {time.time()-t0:.0f}s")
v = open("data/v2_valid.txt", "rb").read().decode("utf-8")
parts = v.split(END)
rt = END.join(tk.decode(tk.encode(p).ids) for p in parts[:2000])
print("valid round trip (first 2000 stories) exact:", rt == END.join(parts[:2000]))
