// Replay the saved observations through a second observer implementation.
// This does not execute SQLite again and is not an independent human review.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import zlib from 'node:zlib';
const sabotage = process.argv.includes('--sabotage');
const directory = process.argv.slice(2).find(a => a !== '--sabotage') ?? 'results';
const summary = JSON.parse(fs.readFileSync(path.join(directory, 'summary.json'), 'utf8'));
const plain = path.join(directory, 'cases.jsonl');
const bytes = fs.existsSync(plain) ? fs.readFileSync(plain) : zlib.gunzipSync(fs.readFileSync(plain+'.gz'));
assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), summary.cases_sha256);
const counters = Object.fromEntries(Object.keys(summary.counts).map(name => [name, {n:0,errors:0,fidelity_loss:0,stable:0,stable_and_lossy:0}]));
const toBits = value => {
  const b = Buffer.alloc(8);
  b.writeDoubleBE(value);
  return b.toString('hex');
};
let rows = 0;
let observerDisagreements = 0;
const seen = new Set();
for (const line of bytes.toString('utf8').trimEnd().split('\n')) {
  const row = JSON.parse(line);
  assert.equal(row.id, rows++);
  assert(!seen.has(row.bits));
  seen.add(row.bits);
  assert.equal(toBits(JSON.parse(row.input)[0]), row.bits);
  for (const [name, outcome] of Object.entries(row.outcomes)) {
    if (sabotage && row.id === 0 && name === 'sqlite_numeric') outcome.fidelity_loss = !outcome.fidelity_loss;
    const c = counters[name];
    c.n++;
    if ('error' in outcome) { c.errors++; continue; }
    const parsed = JSON.parse(outcome.first);
    const preserved = Array.isArray(parsed) && parsed.length === 1 && typeof parsed[0] === 'number' && Number.isFinite(parsed[0]) && toBits(parsed[0]) === row.bits;
    const lossy = !preserved;
    const stable = outcome.first === outcome.second;
    if (lossy !== outcome.fidelity_loss || stable !== outcome.stable) observerDisagreements++;
    c.fidelity_loss += Number(lossy);
    c.stable += Number(stable);
    c.stable_and_lossy += Number(stable && lossy);
  }
}
assert.equal(rows, summary.sample_size);
if (observerDisagreements !== 0) {
  process.stderr.write('GATE: FAIL observation mismatch\n');
  process.exit(1);
}
assert.deepEqual(counters, summary.counts);
const result = {rows, observerDisagreements, counts:counters, node:process.version, subjectRerun:false};
process.stdout.write(JSON.stringify(result,null,2)+'\n');
