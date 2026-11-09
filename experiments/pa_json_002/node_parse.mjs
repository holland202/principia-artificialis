import fs from 'node:fs';
const cases = JSON.parse(fs.readFileSync(0,'utf8'));
function parse(token) {
  try {
    const value = JSON.parse(token);
    if (typeof value !== 'number') return {error:'not numeric'};
    const buffer = Buffer.alloc(8);
    buffer.writeDoubleBE(value);
    return {bits:buffer.toString('hex')};
  } catch(e) { return {error:e.name+': '+e.message}; }
}
const rows = cases.map(row=>({id:row.id,baseline:parse(row.baseline),transformed:parse(row.token)}));
process.stdout.write(JSON.stringify({node:process.version,rows}));
