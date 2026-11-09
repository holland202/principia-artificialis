#!/usr/bin/env python3
"""note080 Python-side observers. Reads tokens (one per line) and prints, for each observer and token index:
  <observer>\t<index>\tOK\t<16 hex bits>   or   <observer>\t<index>\tERR\t<exception class>   or   ...\tOTHER\t<type>
An int or Decimal result is printed as EXACT\t<str(value)> so the driver can compare it exactly.
Run inside the venv that holds the third-party packages; versions are printed first.
"""
import json, sqlite3, struct, sys
from decimal import Decimal
import importlib.metadata as md

import duckdb, msgspec, orjson, rapidjson, simdjson, simplejson, ujson, yyjson  # noqa: E401

PKGS = ["orjson", "ujson", "simplejson", "python-rapidjson", "pysimdjson", "msgspec", "yyjson", "duckdb"]
DUCK = duckdb.connect()
SQL = sqlite3.connect(":memory:")


def sp(tok):
    return simdjson.Parser().parse(tok.encode())


OBSERVERS = {
    "python-json": json.loads,
    "simplejson": simplejson.loads,
    "ujson": ujson.loads,
    "orjson": orjson.loads,
    "python-rapidjson": rapidjson.loads,
    "pysimdjson": sp,
    "msgspec": msgspec.json.decode,
    "yyjson": lambda t: yyjson.Document(t).as_obj,
    "duckdb-cast": lambda t: DUCK.execute("SELECT CAST(? AS DOUBLE)", [t]).fetchone()[0],
    "duckdb-json": lambda t: DUCK.execute("SELECT CAST(CAST(? AS JSON) AS DOUBLE)", [t]).fetchone()[0],
    "sqlite-system-cast": lambda t: SQL.execute("SELECT CAST(? AS REAL)", (t,)).fetchone()[0],
    "sqlite-system-json": lambda t: SQL.execute("SELECT json_extract(?, '$')", (t,)).fetchone()[0],
}


def main(path):
    toks = open(path, encoding="ascii").read().split("\n")[:-1]
    print("#versions\t" + json.dumps({**{p: md.version(p) for p in PKGS}, "python": sys.version.split()[0],
                                       "sqlite-system": sqlite3.sqlite_version}, sort_keys=True))
    for name, fn in OBSERVERS.items():
        for i, t in enumerate(toks):
            try:
                v = fn(t)
            except BaseException as e:  # noqa: BLE001 - every refusal is recorded, none is hidden
                print(f"{name}\t{i}\tERR\t{type(e).__name__}")
                continue
            if isinstance(v, float):
                print(f"{name}\t{i}\tOK\t{struct.unpack('>Q', struct.pack('>d', v))[0]:016x}")
            elif isinstance(v, (int, Decimal)) and not isinstance(v, bool):
                print(f"{name}\t{i}\tEXACT\t{v}")
            else:
                print(f"{name}\t{i}\tOTHER\t{type(v).__name__}")


if __name__ == "__main__":
    main(sys.argv[1])
