import assert from 'node:assert/strict';
const base = process.env.RACETIME_URL || 'http://localhost:3000';
function client() {
  let cookie = '';
  return async (path, body) => {
    const r = await fetch(`${base}/api/${path}`, {
      method: body ? 'POST' : 'GET',
      headers: { cookie, 'Content-Type': 'application/json' },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    cookie = r.headers.get('set-cookie')?.split(';')[0] || cookie;
    return { status: r.status, data: await r.json() };
  };
}
const a = client(),
  b = client();
await a('workspace');
await b('workspace');
const source = {
  title: 'API smoke — synthetic live fixture',
  url: '',
  kind: 'live',
  duration: 1000,
  availableStart: 0,
  availableEnd: 100,
};
const imported = await a('sources', {
  source,
  format: 'json',
  text: JSON.stringify([
    {
      id: 'one',
      start: 10,
      end: 20,
      text: 'A runner reaches the fictional aid station.',
    },
  ]),
});
assert.equal(imported.status, 201);
const id = imported.data.source.id;
const query = {
  sourceId: id,
  start: 0,
  end: 100,
  asOf: 100,
  question: 'What happened?',
};
const run = await a('recap', query);
assert.equal(run.status, 200);
assert.equal(run.data.run.findings.length, 1);
assert.equal((await b('recap', query)).status, 400);
assert.equal(
  (await b('review', { id: run.data.run.id, decision: 'approved' })).status,
  400,
);
const approved = await a('review', {
  id: run.data.run.id,
  decision: 'approved',
});
assert.equal(approved.data.run.review, 'approved');
const next = [
  {
    id: 'two',
    start: 110,
    end: 120,
    text: 'Another synthetic runner arrives.',
  },
];
const append = await a('sources', {
  appendTo: id,
  revision: 1,
  availableEnd: 200,
  format: 'json',
  text: JSON.stringify(next),
});
assert.equal(append.data.source.revision, 2);
assert.equal(
  (
    await a('sources', {
      appendTo: id,
      revision: 1,
      availableEnd: 300,
      format: 'json',
      text: JSON.stringify([{ ...next[0], id: 'three' }]),
    })
  ).status,
  400,
);
const latest = await a('recap', { ...query, end: 200, asOf: 200 });
assert.equal(latest.data.run.findings.length, 2);
assert.equal(latest.data.run.sourceRevision, 2);
assert.equal((await a('recap', { ...query, end: 250, asOf: 250 })).status, 400);
const saved = await a('workspace');
assert.ok(
  saved.data.history.some(
    (r) => r.id === run.data.run.id && r.review === 'approved',
  ),
);
console.log(
  'API smoke passed: import, recap, isolation, review, append, revision conflict, coverage validation, persisted history.',
);
