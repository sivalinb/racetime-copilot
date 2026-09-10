import { Annotation, StateGraph, START, END } from '@langchain/langgraph';
import {
  querySchema,
  playbackUrl,
  type Query,
  type Evidence,
  type Source,
  type Recap,
  type TraceStep,
} from './contracts';
import {
  retrieve,
  eligible,
  conflicts,
  isUnsafeInstruction,
} from './retrieval';
import { WeightedLRU } from './cache';
const cache = new WeightedLRU<Recap>();
export function routeQuestion(q: string, runner = '') {
  if (/compare|versus|difference/i.test(q)) return 'compare';
  if (/confirm|verify|conflict|really|true/i.test(q)) return 'verify';
  if (runner || /runner|bib|where is|follow /i.test(q)) return 'runner';
  return 'recap';
}
const State = Annotation.Root({
  q: Annotation<Query>(),
  source: Annotation<Source>(),
  events: Annotation<Evidence[]>(),
  selected: Annotation<Evidence[]>(),
  route: Annotation<string>(),
  attempts: Annotation<number>(),
  failed: Annotation<boolean>(),
  trace: Annotation<TraceStep[]>({
    reducer: (a, b) => [...a, ...b],
    default: () => [],
  }),
});
const graph = new StateGraph(State)
  .addNode('route_intent', (s) => ({
    route: routeQuestion(s.q.question, s.q.runner),
    attempts: 0,
    trace: [
      {
        name: 'route',
        status: 'ok',
        durationMs: 0,
        detail: 'Deterministic intent routing; no language model is connected.',
      },
    ],
  }))
  .addNode('retrieve', (s) => {
    const t = performance.now();
    const attempts = s.attempts + 1;
    if (s.q.injectFailure && attempts === 1)
      return {
        failed: true,
        attempts,
        trace: [
          {
            name: 'retrieve',
            status: 'retry',
            durationMs: performance.now() - t,
            detail: 'Simulated transient retrieval failure; one bounded retry.',
          },
        ],
      };
    const selected = retrieve(s.events, s.q);
    return {
      selected,
      failed: false,
      attempts,
      trace: [
        {
          name: 'retrieve',
          status: 'ok',
          durationMs: performance.now() - t,
          detail: `${selected.length} evidence records retrieved using lexical and hashed-vector scores within the interval and spoiler cutoff.`,
        },
      ],
    };
  })
  .addNode('verify', (s) => {
    const selected = [...(s.selected || [])];
    const keys = new Set(selected.map((e) => e.claimKey).filter(Boolean));
    for (const e of eligible(s.events, s.q)) {
      if (
        e.claimKey &&
        keys.has(e.claimKey) &&
        !selected.some((x) => x.id === e.id)
      )
        selected.push(e);
    }
    const clean = selected.filter((e) => !isUnsafeInstruction(e.text));
    return {
      selected: clean.sort((a, b) => a.start - b.start),
      trace: [
        {
          name: 'verify',
          status: conflicts(clean).length ? 'review' : 'ok',
          durationMs: 0,
          detail: `Checked related claims within the same time bounds; excluded ${selected.length - clean.length} suspicious instruction records. Source statements remain unverified reports.`,
        },
      ],
    };
  })
  .addConditionalEdges('retrieve', (s) => (s.failed ? 'retry' : 'verify'), {
    retry: 'retrieve',
    verify: 'verify',
  })
  .addEdge(START, 'route_intent')
  .addEdge('route_intent', 'retrieve')
  .addEdge('verify', END)
  .compile();
export async function runRecap(
  source: Source,
  events: Evidence[],
  input: Query,
): Promise<Recap> {
  const t = performance.now();
  const q = querySchema.parse(input);
  if (q.sourceId !== source.id) throw new Error('Source mismatch.');
  if (
    q.start < source.availableStart ||
    q.end > source.availableEnd ||
    q.asOf > source.availableEnd
  )
    throw new Error(
      `Choose an interval and spoiler cutoff within available coverage (${source.availableStart}–${source.availableEnd} seconds).`,
    );
  const key = JSON.stringify([source.id, source.revision, q]);
  const cached = cache.get(key);
  if (cached)
    return {
      ...cached,
      id: crypto.randomUUID(),
      review: 'pending',
      createdAt: new Date().toISOString(),
      cacheHit: true,
      latencyMs: performance.now() - t,
      trace: [
        {
          name: 'cache',
          status: 'hit',
          durationMs: 0,
          detail: 'Revision-aware cache reused this exact request.',
        },
      ],
    };
  const state = await graph.invoke(
    { q, source, events, trace: [] },
    {
      runName: 'racetime-recap',
      tags: ['extractive'],
      metadata: { source_id: source.id, revision: source.revision },
    },
  );
  const selected = state.selected || [];
  const cs = conflicts(selected);
  const warnings = [
    'This is an extractive evidence recap. A language model has not watched the video.',
  ];
  if (source.provenance === 'fictional_demo')
    warnings.push(
      'All race names, runners, and observations in this source are fictional demonstration data.',
    );
  if (cs.length)
    warnings.push(
      'Conflicting source claims require review. This recap does not declare an official race position.',
    );
  if (selected.length === 0)
    warnings.push(
      'Insufficient evidence for this request. Import relevant timestamped observations or choose another interval.',
    );
  if (
    events.some(
      (e) =>
        e.start < q.end &&
        e.end > q.start &&
        (e.start < q.start || e.end > q.end),
    )
  )
    warnings.push(
      'Records crossing an interval boundary were excluded to avoid revealing content outside your selection.',
    );
  if (selected.length >= 60)
    warnings.push(
      'Retrieval is capped at 60 records. Narrow the interval for a more complete recap.',
    );
  const result: Recap = {
    id: crypto.randomUUID(),
    sourceId: source.id,
    sourceTitle: source.title,
    sourceRevision: source.revision,
    start: q.start,
    end: q.end,
    asOf: q.asOf,
    question: q.question,
    route: state.route,
    routerMode: 'rules',
    mode: 'extractive',
    status: cs.length
      ? 'needs_review'
      : selected.length
        ? 'ready'
        : 'insufficient_evidence',
    findings: selected.map((e) => ({
      id: e.id,
      start: e.start,
      end: e.end,
      text: e.text,
      kind: e.kind,
      url: playbackUrl(source.url, e.start),
      runner: e.runner,
      support: 'source_report',
    })),
    warnings,
    conflicts: cs,
    trace: [
      ...state.trace,
      {
        name: 'compose',
        status: 'ok',
        durationMs: 0,
        detail:
          'Copied bounded evidence with timestamps; no inferred race facts.',
      },
      {
        name: 'human_review',
        status: 'pending',
        durationMs: 0,
        detail: 'User can approve or reject this saved recap before sharing.',
      },
    ],
    latencyMs: performance.now() - t,
    retrievalMs: state.trace
      .filter((e) => e.name === 'retrieve')
      .reduce((a, b) => a + b.durationMs, 0),
    cacheHit: false,
    createdAt: new Date().toISOString(),
    review: 'pending',
  };
  cache.set(key, result);
  return result;
}
export const cacheMetrics = () => cache.stats();
