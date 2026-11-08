import fs from 'node:fs';
const documents = JSON.parse(fs.readFileSync(0, 'utf8'));
const rows = documents.map(s => {
  try {
    const first = JSON.stringify(JSON.parse(s));
    const second = JSON.stringify(JSON.parse(first));
    return {first, second};
  } catch (e) {
    return {error: `${e.name}: ${e.message}`};
  }
});
process.stdout.write(JSON.stringify({versions: process.versions, rows}));
