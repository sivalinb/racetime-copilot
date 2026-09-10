/** Evaluate frozen expectations; never regenerate golden answers from the candidate. */
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';
import { runRecap } from '../lib/workflow';
import { querySchema, eventSchema, type TraceStep } from '../lib/contracts';
import { demoSource } from '../data/demo';

const base = new URL('./', import.meta.url);
const root = new URL('../', base);
const read = (path: string) => readFileSync(new URL(path, base));
const hash = (bytes: Buffer) =>
  createHash('sha256').update(bytes).digest('hex');
const write = (path: string, data: unknown) =>
  writeFileSync(new URL(path, base), JSON.stringify(data, null, 2) + '\n');
const manifest = JSON.parse(read('datasets/manifest.json').toString());
for (const [name, spec] of Object.entries(manifest.datasets) as [
  string,
  { sha256: string },
][]) {
  if (hash(read('datasets/' + name)) !== spec.sha256)
    throw new Error(
      `Frozen dataset checksum mismatch: ${name}. Review and version data changes explicitly.`,
    );
}
const cases = z
  .array(
    z.object({
      id: z.string().min(1),
      name: z.string().min(1),
      q: querySchema,
      events: z.array(eventSchema),
      expected: z.array(z.string()),
    }),
  )
  .parse(JSON.parse(read('datasets/evidence-golden-v1.json').toString()));
if (
  cases.length !== 40 ||
  new Set(cases.map((c) => c.id)).size !== cases.length
)
  throw new Error('Expected 40 uniquely identified golden cases.');
for (const c of cases) {
  if (
    new Set(c.events.map((e) => e.id)).size !== c.events.length ||
    new Set(c.expected).size !== c.expected.length ||
    c.expected.some((id) => !c.events.some((e) => e.id === id))
  )
    throw new Error(`Invalid evidence IDs in ${c.id}`);
}
const category = (id: string) =>
  id.startsWith('contained-')
    ? 'exact_containment'
    : id.startsWith('clipped-')
      ? 'crossing_boundary'
      : id === 'delayed'
        ? 'availability_cutoff'
        : id === 'untrusted-instruction'
          ? 'source_instruction'
          : 'authored_scenarios';
const rows: {
  id: string;
  category: string;
  expected: string[];
  actual: string[];
  baseline: string[];
  pass: boolean;
  baselinePass: boolean;
  latencyMs: number;
  trace: TraceStep[];
}[] = [];
for (const c of cases) {
  const source = { ...demoSource, id: 'benchmark-' + c.id };
  const result = await runRecap(source, c.events, {
    ...c.q,
    sourceId: source.id,
  });
  const actual = result.findings.map((e) => e.id).sort();
  const expected = [...c.expected].sort();
  const baseline = c.events
    .filter((e) => e.start < c.q.end && e.end > c.q.start)
    .map((e) => e.id)
    .sort();
  rows.push({
    id: c.id,
    category: category(c.id),
    expected,
    actual,
    baseline,
    pass: JSON.stringify(actual) === JSON.stringify(expected),
    baselinePass: JSON.stringify(baseline) === JSON.stringify(expected),
    latencyMs: result.latencyMs,
    trace: result.trace,
  });
}
const times = rows.map((r) => r.latencyMs).sort((a, b) => a - b);
const provenanceFiles = [
  'lib/workflow.ts',
  'lib/retrieval.ts',
  'lib/cache.ts',
  'lib/contracts.ts',
  'data/demo.ts',
  'evals-observability/run.ts',
];
const codeHashes = Object.fromEntries(
  provenanceFiles.map((p) => [p, hash(readFileSync(new URL(p, root)))]),
);
const groups = [...new Set(rows.map((r) => r.category))].map((name) => {
  const group = rows.filter((r) => r.category === name);
  return {
    category: name,
    count: group.length,
    passed: group.filter((r) => r.pass).length,
    baselinePassed: group.filter((r) => r.baselinePass).length,
  };
});
const report = {
  generatedAt: new Date().toISOString(),
  datasetVersion: 'v1',
  datasetSha256: manifest.datasets['evidence-golden-v1.json'].sha256,
  sourceCommit: execFileSync('git', ['rev-parse', 'HEAD'], {
    cwd: fileURLToPath(root),
    encoding: 'utf8',
  }).trim(),
  workingTreeDirty: Boolean(
    execFileSync('git', ['status', '--porcelain'], {
      cwd: fileURLToPath(root),
      encoding: 'utf8',
    }).trim(),
  ),
  codeHashes,
  runtime: {
    node: process.version,
    platform: process.platform,
    arch: process.arch,
  },
  scope:
    'Frozen authored synthetic evidence selection; no video model calls or real-race accuracy claim.',
  metric:
    'Exact equality of sorted selected evidence IDs to frozen expected IDs',
  baseline:
    'Naive temporal overlap; no availability, full containment or source-instruction filtering',
  count: rows.length,
  passed: rows.filter((r) => r.pass).length,
  baselinePassed: rows.filter((r) => r.baselinePass).length,
  p50Ms: times[Math.ceil(times.length * 0.5) - 1],
  p95Ms: times[Math.ceil(times.length * 0.95) - 1],
  latencyScope:
    'One local in-process run per case; nearest-rank percentiles; excludes UI, network and video processing.',
  providerCalls: 0,
  providerCostUSD: 0,
  costScope:
    'No paid provider calls; excludes hardware, energy and development costs.',
  groups,
  cases: rows,
};
write('benchmarks/evidence-latest.json', report);

// Observable behavior on fictional evidence: normal conflict, one retry, then a cache hit.
const c = cases.find((c) => c.id === 'conflict')!;
const source = { ...demoSource, id: 'observability-conflict' };
const q = { ...c.q, sourceId: source.id };
const conflict = await runRecap(source, c.events, q);
const retry = await runRecap(source, c.events, { ...q, injectFailure: true });
const cached = await runRecap(source, c.events, { ...q, injectFailure: true });
const traceChecks = {
  conflictFlagged: conflict.conflicts.length > 0,
  retryRecorded: retry.trace.some((t) => t.status === 'retry'),
  retrievalRecovered: retry.trace.some(
    (t) => t.name === 'retrieve' && t.status === 'ok',
  ),
  cacheHitRecorded:
    cached.cacheHit &&
    cached.trace.some((t) => t.name === 'cache' && t.status === 'hit'),
};
const sample = (r: typeof conflict) => ({
  status: r.status,
  latencyMs: r.latencyMs,
  cacheHit: r.cacheHit,
  conflicts: r.conflicts,
  trace: r.trace,
});
write('observability/examples/evidence-demo.json', {
  provenance:
    'Actual local runs on fictional Canyon Relay observations; no provider calls.',
  generatedAt: report.generatedAt,
  checks: traceChecks,
  conflict: sample(conflict),
  retry: sample(retry),
  cacheHit: sample(cached),
});
console.log(
  JSON.stringify(
    {
      count: report.count,
      passed: report.passed,
      baselinePassed: report.baselinePassed,
      p50Ms: report.p50Ms,
      p95Ms: report.p95Ms,
      groups,
      traceChecks,
    },
    null,
    2,
  ),
);
if (
  report.passed !== report.count ||
  Object.values(traceChecks).some((value) => !value)
)
  process.exitCode = 1;
