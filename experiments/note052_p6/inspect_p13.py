#!/usr/bin/env python3
"""Describe the P13 cases after the run (descriptive, not a prediction). Standard library only.

  python -I experiments/note052_p6/inspect_p13.py OUT    OUT is run_p13.py's output folder
"""
import ast, json, os, sys

out = sys.argv[1]
for c in json.load(open(f"{out}/census.json"))["not_same"]:
    f = f"{out}/filtered/{c['repo'].replace('/', '__')}/{c['path']}"
    b = open(f, "rb").read()
    print(f"{c['repo']} {c['path']}: class {c['class']}")
    try:
        b.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"  first invalid UTF-8 byte: offset {e.start}, line {b[:e.start].count(b'\n') + 1}")
    print(f"  encoding declaration in lines 1-2: {b'coding' in b''.join(b.split(b'\n')[:2])}")
    for enc in ("gbk", "latin-1"):
        try:
            b.decode(enc)
            print(f"  decodes as {enc}: yes")
        except UnicodeDecodeError:
            print(f"  decodes as {enc}: no")
    try:
        compile(b, f, "exec")
        print("  python compile(bytes): OK")
    except SyntaxError as e:
        print(f"  python compile(bytes): {type(e).__name__}: {str(e)[:60]}")
k3 = f"{out}/control/K3/verify_output.py"
compile(open(k3, "rb").read(), k3, "exec")
print("K3 file: python compile(bytes): OK")
try:
    ast.parse(open(k3, encoding="utf-8", errors="replace").read())
    print("K3 file: ast.parse of A's text: OK")
except SyntaxError as e:
    print(f"K3 file: ast.parse of A's text: {e.msg}")
