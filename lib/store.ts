import { env } from 'cloudflare:workers';
import type { Source, Evidence, Recap } from './contracts';
import { demoSource, demoEvents } from '../data/demo';
let initialized: Promise<unknown> | undefined;
const db = () => env.DB;
export async function initialize() {
  initialized ??= db()
    .batch(
      [
        'CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,session TEXT NOT NULL,payload TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 1)',
        'CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY,session TEXT NOT NULL,source_id TEXT NOT NULL,start REAL NOT NULL,end REAL NOT NULL,payload TEXT NOT NULL)',
        'CREATE INDEX IF NOT EXISTS idx_evidence_source_time ON evidence(session,source_id,start)',
        'CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,session TEXT NOT NULL,source_id TEXT NOT NULL,created_at TEXT NOT NULL,payload TEXT NOT NULL)',
        'CREATE INDEX IF NOT EXISTS idx_runs_session_created ON runs(session,created_at)',
      ].map((sql) => db().prepare(sql)),
    )
    .catch((e) => {
      initialized = undefined;
      throw e;
    });
  await initialized;
}
export function session(req: Request) {
  const old = req.headers
    .get('cookie')
    ?.match(/(?:^|; )racetime_session=([a-f0-9-]{36})(?:;|$)/)?.[1];
  return { id: old || crypto.randomUUID(), fresh: !old };
}
export function response(
  data: unknown,
  s: { id: string; fresh: boolean },
  status = 200,
) {
  return Response.json(data, {
    status,
    headers: {
      'Cache-Control': 'no-store',
      ...(s.fresh
        ? {
            'Set-Cookie': `racetime_session=${s.id}; Path=/; HttpOnly; SameSite=Strict; Max-Age=604800`,
          }
        : {}),
    },
  });
}
export async function listSources(owner: string) {
  await initialize();
  const rows = await db()
    .prepare('SELECT payload,revision FROM sources WHERE session=?')
    .bind(owner)
    .all<{ payload: string; revision: number }>();
  return [
    demoSource,
    ...rows.results.map((r) => ({
      ...JSON.parse(r.payload),
      revision: r.revision,
    })),
  ] as Source[];
}
export async function loadSource(owner: string, id: string) {
  if (id === 'demo') return { source: demoSource, events: demoEvents };
  await initialize();
  const row = await db()
    .prepare('SELECT payload,revision FROM sources WHERE session=? AND id=?')
    .bind(owner, id)
    .first<{ payload: string; revision: number }>();
  if (!row) throw new Error('Source not found in this browser session.');
  const es = await db()
    .prepare(
      'SELECT payload FROM evidence WHERE session=? AND source_id=? ORDER BY start',
    )
    .bind(owner, id)
    .all<{ payload: string }>();
  return {
    source: { ...JSON.parse(row.payload), revision: row.revision } as Source,
    events: es.results.map((r) => JSON.parse(r.payload)) as Evidence[],
  };
}
export async function addSource(
  owner: string,
  source: Source,
  events: Evidence[],
) {
  await initialize();
  const count = await db()
    .prepare('SELECT COUNT(*) AS n FROM sources WHERE session=?')
    .bind(owner)
    .first<{ n: number }>();
  if ((count?.n || 0) >= 20)
    throw new Error('This browser session already has 20 sources.');
  await db().batch([
    db()
      .prepare('INSERT INTO sources VALUES(?,?,?,?)')
      .bind(source.id, owner, JSON.stringify(source), source.revision),
    ...events.map((e) =>
      db()
        .prepare('INSERT INTO evidence VALUES(?,?,?,?,?,?)')
        .bind(
          `${source.id}:${e.id}`,
          owner,
          source.id,
          e.start,
          e.end,
          JSON.stringify(e),
        ),
    ),
  ]);
}
export async function appendSource(
  owner: string,
  id: string,
  expectedRevision: number,
  availableEnd: number,
  events: Evidence[],
) {
  const old = await loadSource(owner, id);
  if (old.source.kind !== 'live' || id === 'demo')
    throw new Error('Append requires an imported live source.');
  if (old.source.revision !== expectedRevision)
    throw new Error('Revision conflict. Reload before appending.');
  const ids = new Set(old.events.map((e) => e.id));
  if (events.some((e) => ids.has(e.id)))
    throw new Error('An evidence ID already exists.');
  const source = {
    ...old.source,
    availableEnd,
    revision: expectedRevision + 1,
  };
  if (availableEnd < old.source.availableEnd || availableEnd > source.duration)
    throw new Error('Live coverage must advance within source duration.');
  validateEvents(source, events);
  const results = await db().batch([
    ...events.map((e) =>
      db()
        .prepare(
          'INSERT INTO evidence SELECT ?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM sources WHERE id=? AND session=? AND revision=?)',
        )
        .bind(
          `${id}:${e.id}`,
          owner,
          id,
          e.start,
          e.end,
          JSON.stringify(e),
          id,
          owner,
          expectedRevision,
        ),
    ),
    db()
      .prepare(
        'UPDATE sources SET payload=?,revision=? WHERE id=? AND session=? AND revision=?',
      )
      .bind(
        JSON.stringify(source),
        source.revision,
        id,
        owner,
        expectedRevision,
      ),
  ]);
  if (!results.at(-1)?.meta.changes)
    throw new Error('Revision conflict. Reload before appending.');
  return source;
}
export function validateEvents(source: Source, events: Evidence[]) {
  if (!events.length) throw new Error('No evidence supplied.');
  if (new Set(events.map((e) => e.id)).size !== events.length)
    throw new Error('Duplicate evidence IDs.');
  if (
    events.some(
      (e) => e.start < source.availableStart || e.end > source.availableEnd,
    )
  )
    throw new Error('Evidence lies outside declared source coverage.');
  if (events.some((e) => e.availableAt !== undefined && e.availableAt < e.end))
    throw new Error('availableAt must be at or after the evidence end.');
  if (source.url && !source.url.startsWith('https://'))
    throw new Error('Invalid video URL.');
}
export async function saveRun(owner: string, run: Recap) {
  await initialize();
  await db()
    .prepare('INSERT INTO runs VALUES(?,?,?,?,?)')
    .bind(run.id, owner, run.sourceId, run.createdAt, JSON.stringify(run))
    .run();
  await db()
    .prepare(
      'DELETE FROM runs WHERE session=? AND id NOT IN (SELECT id FROM runs WHERE session=? ORDER BY created_at DESC LIMIT 100)',
    )
    .bind(owner, owner)
    .run();
}
export async function history(owner: string) {
  await initialize();
  const rows = await db()
    .prepare(
      'SELECT payload FROM runs WHERE session=? ORDER BY created_at DESC LIMIT 20',
    )
    .bind(owner)
    .all<{ payload: string }>();
  return rows.results.map((r) => JSON.parse(r.payload)) as Recap[];
}
export async function reviewRun(
  owner: string,
  id: string,
  decision: 'approved' | 'rejected',
) {
  await initialize();
  const row = await db()
    .prepare('SELECT payload FROM runs WHERE session=? AND id=?')
    .bind(owner, id)
    .first<{ payload: string }>();
  if (!row) throw new Error('Run not found in this browser session.');
  const run: Recap = { ...JSON.parse(row.payload), review: decision };
  await db()
    .prepare('UPDATE runs SET payload=? WHERE session=? AND id=?')
    .bind(JSON.stringify(run), owner, id)
    .run();
  return run;
}
