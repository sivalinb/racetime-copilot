import type { Evidence, Query } from './contracts';
const STOP = new Set(
  'the a an in on at to of and or is was were what happened me this that for please summarize recap catch up interval last minutes hours between'.split(
    ' ',
  ),
);
export function tokens(text: string) {
  return (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter(
    (x) => !STOP.has(x),
  );
}
export function embed(text: string) {
  const out = Array(128).fill(0);
  for (const word of tokens(text)) {
    let h = 2166136261;
    for (const c of word) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
    out[(h >>> 0) % 128] += 1;
  }
  const norm = Math.hypot(...out) || 1;
  return out.map((x) => x / norm);
}
export function eligible(events: Evidence[], q: Query) {
  return events.filter(
    (e) =>
      e.start >= q.start &&
      e.end <= q.end &&
      e.end <= q.asOf &&
      (e.availableAt ?? e.end) <= q.asOf,
  );
}
export function retrieve(events: Evidence[], q: Query, broad = false) {
  let pool = eligible(events, q);
  if (q.runner)
    pool = pool.filter((e) =>
      (e.runner || e.text).toLowerCase().includes(q.runner.toLowerCase()),
    );
  const terms = tokens(q.question);
  const generic =
    /catch|summari|recap|what happened|overview/i.test(q.question) &&
    terms.length < 3;
  const qv = embed(q.question);
  const lengths = pool.map((e) => tokens(e.text).length);
  const avg = lengths.reduce((a, b) => a + b, 0) / (pool.length || 1) || 1;
  const scored = pool
    .map((e, i) => {
      const words = tokens(e.text);
      let bm25 = 0;
      for (const t of terms) {
        const tf = words.filter((w) => w === t).length;
        const df = pool.filter((p) => tokens(p.text).includes(t)).length;
        const idf = Math.log(1 + (pool.length - df + 0.5) / (df + 0.5));
        bm25 +=
          (idf * (tf * 2.2)) / (tf + 1.2 * (0.25 + (0.75 * lengths[i]) / avg));
      }
      const ev = embed(e.text);
      const dense = ev.reduce((s, n, j) => s + n * qv[j], 0);
      return { e, score: bm25 + dense * 0.25, lexical: bm25 };
    })
    .filter((x) => broad || generic || !terms.length || x.lexical > 0)
    .sort((a, b) => b.score - a.score);
  return scored
    .slice(0, 60)
    .map((x) => x.e)
    .sort((a, b) => a.start - b.start);
}
export function conflicts(events: Evidence[]) {
  const groups = new Map<string, Evidence[]>();
  for (const e of events) {
    if (!e.claimKey || !e.claimValue) continue;
    const k = e.claimKey;
    groups.set(k, [...(groups.get(k) || []), e]);
  }
  return [...groups]
    .filter(([, es]) => new Set(es.map((e) => e.claimValue)).size > 1)
    .map(([key, es]) => ({
      key,
      ids: es.map((e) => e.id),
      values: [...new Set(es.map((e) => e.claimValue!))],
    }));
}
export function isUnsafeInstruction(text: string) {
  return /ignore (?:all |previous |prior )?instructions|reveal.*(?:secret|key)|system prompt|send.*(?:password|token)/i.test(
    text,
  );
}
