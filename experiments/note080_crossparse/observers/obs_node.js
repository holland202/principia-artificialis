// note080 Node observer: JSON.parse and Number() on each token (one per line). Same output format as obs_python.py.
const fs = require("fs");
const toks = fs.readFileSync(process.argv[2], "ascii").split("\n").slice(0, -1);
console.log("#versions\t" + JSON.stringify({ node: process.version, v8: process.versions.v8 }));
const bits = (x) => { const b = Buffer.alloc(8); b.writeDoubleBE(x); return b.toString("hex"); };
for (const [name, fn] of [["node-JSON.parse", (t) => JSON.parse(t)], ["node-Number", (t) => Number(t)]]) {
  toks.forEach((t, i) => {
    let v;
    try { v = fn(t); } catch (e) { console.log(`${name}\t${i}\tERR\t${e.name}`); return; }
    if (typeof v === "number") console.log(`${name}\t${i}\tOK\t${bits(v)}`);
    else console.log(`${name}\t${i}\tOTHER\t${typeof v}`);
  });
}
