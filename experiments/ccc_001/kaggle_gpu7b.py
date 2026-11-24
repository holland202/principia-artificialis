"""CCC-001 GPU run of GPU7B_AMENDMENT.md: stage Q and LONGCTX on Qwen2.5-7B-Instruct, Kaggle 2x T4, float16.

Paste into one Kaggle notebook cell (Settings: Accelerator "GPU T4 x2", Internet on):

    !git clone -q https://github.com/holland202/principia-artificialis /kaggle/working/pa
    !cd /kaggle/working/pa && git checkout -q claude/ccc-001-rendering && python experiments/ccc_001/kaggle_gpu7b.py

It installs transformers 5.24.0, downloads the pinned revision, checks the four shard SHA-256s (stops on any
mismatch), runs the registered steps in order and writes every log and JSON to /kaggle/working/ccc001_gpu7b/,
zipped as /kaggle/working/ccc001_gpu7b.zip. The last lines it prints are the summary to paste back.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
EXP = os.path.join(REPO, "experiments/ccc_001")
OUT = "/kaggle/working/ccc001_gpu7b" if os.path.isdir("/kaggle/working") else os.path.join(REPO, "ccc001_gpu7b")
MODEL = "Qwen/Qwen2.5-7B-Instruct"
REVISION = "a09a35458c702b33eeacc393d103063234e8bc28"
SHARDS = {  # GPU7B_AMENDMENT.md, from the Hub's LFS metadata
    "model-00001-of-00004.safetensors": "a1333e6293854747c481288ea83b348226af178dd565c49b6f9495ba1966aba7",
    "model-00002-of-00004.safetensors": "f5d25a2772cb825164a2a2c0fb6d51a87e282abf21e4dd75bc5cfb3cd0ea6185",
    "model-00003-of-00004.safetensors": "8efdec4c1bc12317ae1a38dc42b595ce777738a64deea3fcb8a0a91381bcdfd5",
    "model-00004-of-00004.safetensors": "1a72d403cdf0c1ec3cb7f289f17b394a01e64394c2e9b3c0f94dbce3faf879bd",
}
R = "results/ccc_001"
STEPS = [  # (name, cwd, argv), in the registered order
    ("g0", EXP, ["longctx.py", "--g0-only"]),
    ("stageq", REPO, ["experiments/ccc_001/qualify.py", "--json", f"{OUT}/qualify_7b.json"]),
    ("stageq_sabotage", REPO, ["experiments/ccc_001/qualify.py", "--sabotage"]),
    ("longctx_REF", EXP, ["longctx.py", "--length", "REF", "--json", f"{OUT}/longctx_REF_7b.json"]),
    ("longctx_N016", EXP, ["longctx.py", "--length", "N016", "--json", f"{OUT}/longctx_N016_7b.json"]),
    ("longctx_STRESS", EXP, ["longctx.py", "--length", "STRESS", "--json", f"{OUT}/longctx_STRESS_7b.json"]),
    ("longctx_REF_sabotage", EXP, ["longctx.py", "--length", "REF", "--sabotage"]),
]


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def model_dir():
    for d in ("/kaggle/tmp", "/tmp", os.path.expanduser("~")):
        if os.path.isdir(d) and shutil.disk_usage(d).free > 17e9:
            return os.path.join(d, "qwen25-7b-instruct")
    sys.exit("no directory with 17 GB free for the weights")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "runner.txt"), "w")

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "transformers==5.24.0", "accelerate",
                    "huggingface_hub", "jinja2"], check=True)
    import torch
    import transformers
    import accelerate
    say("repo HEAD", sh(f"git -C {REPO} rev-parse HEAD"), "| python", sys.version.split()[0])
    say("torch", torch.__version__, "| cuda", torch.version.cuda, "| transformers", transformers.__version__,
        "| accelerate", accelerate.__version__)
    say("gpus", [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
    if torch.cuda.device_count() < 1:
        sys.exit("no GPU visible: set Accelerator to GPU T4 x2")

    from huggingface_hub import snapshot_download
    md = model_dir()
    t = time.time()
    snapshot_download(MODEL, revision=REVISION, local_dir=md)
    say("downloaded", MODEL, REVISION, "to", md, f"in {time.time() - t:.0f} s")
    for f, want in SHARDS.items():
        got = sha256(os.path.join(md, f))
        say(f, got, "OK" if got == want else "MISMATCH")
        if got != want:
            sys.exit("weight hash mismatch: stopping before any reading (GPU7B_AMENDMENT.md)")

    env = dict(os.environ, CCC_MODEL_DIR=md, CCC_DTYPE="float16", CCC_DEVICE_MAP="auto", PYTHONUNBUFFERED="1")
    summary = []
    for name, cwd, argv in STEPS:
        t = time.time()
        p = subprocess.run([sys.executable] + argv, cwd=cwd, env=env, capture_output=True, text=True)
        out = p.stdout + p.stderr
        open(os.path.join(OUT, f"{name}.txt"), "w").write(out + f"EXIT {p.returncode}\n")
        say(f"== {name}: exit {p.returncode}, {time.time() - t:.0f} s")
        for line in out.splitlines():
            if line.startswith(("G", "Q", "P")) or any(k in line for k in ("VERDICT", "DIGEST", "LONGEST",
                                                                          "QUALIFIES", "SABOTAGE", "Error")):
                say("  " + line)
                summary.append(f"{name}: {line}")
    p = subprocess.run([sys.executable, "longctx_summary.py"] +
                       [os.path.join(OUT, f"longctx_{n}.txt") for n in ("REF", "N016", "STRESS")],
                       cwd=EXP, capture_output=True, text=True)
    open(os.path.join(OUT, "longctx_summary.txt"), "w").write(p.stdout + p.stderr)
    say("== T* summary\n" + p.stdout)
    log.close()
    z = shutil.make_archive(OUT, "zip", OUT)
    print("ZIP", z, "sha256", sha256(z))
    print("Paste the lines from 'repo HEAD' down to here into PR #177, and attach the zip if you can.")


if __name__ == "__main__":
    main()
