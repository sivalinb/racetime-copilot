import { z } from 'zod';
export const eventSchema = z
  .object({
    id: z.string().min(1).max(100),
    start: z.number().nonnegative(),
    end: z.number().nonnegative(),
    text: z.string().min(1).max(4000),
    kind: z
      .enum(['commentary', 'visual', 'timing', 'context'])
      .default('commentary'),
    speaker: z.string().max(120).optional(),
    runner: z.string().max(120).optional(),
    claimKey: z.string().max(120).optional(),
    claimValue: z.string().max(120).optional(),
    supersedes: z.string().max(100).optional(),
    availableAt: z.number().nonnegative().optional(),
  })
  .refine((e) => e.end > e.start, 'Event end must follow start');
export const sourceSchema = z
  .object({
    title: z.string().min(1).max(180),
    url: z.string().max(1000).default(''),
    kind: z.enum(['recorded', 'live']).default('recorded'),
    duration: z.number().positive().max(604800),
    availableStart: z.number().nonnegative().default(0),
    availableEnd: z.number().nonnegative(),
    provenance: z
      .enum(['fictional_demo', 'user_import', 'gemini_video'])
      .default('user_import'),
  })
  .refine(
    (s) => s.availableStart < s.availableEnd && s.availableEnd <= s.duration,
    'Invalid source coverage',
  );
export const querySchema = z
  .object({
    sourceId: z.string().min(1).max(100),
    start: z.number().nonnegative(),
    end: z.number().positive(),
    asOf: z.number().nonnegative(),
    question: z.string().min(1).max(1000),
    runner: z.string().max(120).default(''),
    injectFailure: z.boolean().default(false),
  })
  .refine((q) => q.end > q.start, 'End must be after start')
  .refine(
    (q) => q.end <= q.asOf,
    'Requested interval extends past spoiler boundary',
  );
export type Evidence = z.infer<typeof eventSchema>;
export type Source = z.infer<typeof sourceSchema> & {
  id: string;
  revision: number;
};
export type Query = z.infer<typeof querySchema>;
export type TraceStep = {
  name: string;
  status: string;
  durationMs: number;
  detail: string;
};
export type Finding = {
  id: string;
  start: number;
  end: number;
  text: string;
  kind: Evidence['kind'];
  url: string;
  runner?: string;
  support: 'source_report';
};
export type Recap = {
  id: string;
  sourceId: string;
  sourceTitle: string;
  sourceRevision: number;
  start: number;
  end: number;
  asOf: number;
  question: string;
  route: string;
  routerMode: string;
  mode: string;
  status: 'ready' | 'needs_review' | 'insufficient_evidence';
  findings: Finding[];
  warnings: string[];
  conflicts: { key: string; ids: string[]; values: string[] }[];
  trace: TraceStep[];
  latencyMs: number;
  retrievalMs: number;
  cacheHit: boolean;
  createdAt: string;
  review: 'pending' | 'approved' | 'rejected';
};
export function parseTime(value: string): number {
  const t = value.trim();
  if (!/^\d+(?::[0-5]\d){0,2}$/.test(t))
    throw new Error('Use seconds, MM:SS, or HH:MM:SS.');
  const p = t.split(':').map(Number);
  return p.reduce((a, n) => a * 60 + n, 0);
}
export function formatTime(n: number) {
  const v = Math.max(0, Math.floor(n));
  return [Math.floor(v / 3600), Math.floor(v / 60) % 60, v % 60]
    .map((x) => String(x).padStart(2, '0'))
    .join(':');
}
export function youtubeId(value: string) {
  if (!value) return '';
  const u = new URL(value);
  if (u.protocol !== 'https:') throw new Error('Use an HTTPS YouTube URL.');
  let id = '';
  if (u.hostname === 'youtu.be') id = u.pathname.slice(1);
  else if (
    ['youtube.com', 'www.youtube.com', 'm.youtube.com'].includes(u.hostname)
  )
    id =
      u.searchParams.get('v') ||
      u.pathname.match(/^\/(?:live|embed|shorts)\/([^/]+)/)?.[1] ||
      '';
  else throw new Error('Only YouTube video URLs are supported.');
  if (!/^[\w-]{11}$/.test(id)) throw new Error('Invalid YouTube video ID.');
  return id;
}
export function playbackUrl(url: string, start: number) {
  if (!url) return '';
  const id = youtubeId(url);
  return `https://www.youtube.com/watch?v=${id}&t=${Math.floor(start)}s`;
}
