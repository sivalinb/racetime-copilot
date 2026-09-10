'use client';
import { useCallback, useEffect, useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from '../components/ui/tabs';
import {
  formatTime,
  parseTime,
  youtubeId,
  type Source,
  type Recap,
} from '../lib/contracts';
async function api(path: string, body?: unknown) {
  const res = await fetch(
    `/api/${path}`,
    body
      ? {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }
      : undefined,
  );
  const data = (await res.json()) as {
    error?: string;
    sources: Source[];
    history: Recap[];
    run: Recap;
    source: Source;
  };
  if (!res.ok) throw new Error(data.error || 'Request failed.');
  return data;
}
export default function Home() {
  const [sources, setSources] = useState<Source[]>([]),
    [sourceId, setSourceId] = useState('demo'),
    [runs, setRuns] = useState<Recap[]>([]),
    [run, setRun] = useState<Recap | null>(null),
    [start, setStart] = useState('00:00'),
    [end, setEnd] = useState('15:00'),
    [cutoff, setCutoff] = useState('15:00'),
    [question, setQuestion] = useState('What happened?'),
    [runner, setRunner] = useState(''),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(''),
    [notice, setNotice] = useState(''),
    [seek, setSeek] = useState(0),
    [retry, setRetry] = useState(false);
  const [title, setTitle] = useState('My race broadcast'),
    [url, setUrl] = useState(''),
    [kind, setKind] = useState('recorded'),
    [duration, setDuration] = useState('01:00:00'),
    [coverage, setCoverage] = useState('15:00'),
    [coverageStart, setCoverageStart] = useState('00:00'),
    [format, setFormat] = useState('vtt'),
    [text, setText] = useState(''),
    [append, setAppend] = useState(false);
  const source = sources.find((s) => s.id === sourceId);
  const refresh = useCallback(async () => {
    const data = await api('workspace');
    setSources(data.sources);
    setRuns(data.history);
  }, []);
  useEffect(() => {
    let active = true;
    api('workspace').then(
      (data) => {
        if (active) {
          setSources(data.sources);
          setRuns(data.history);
        }
      },
      (e) => {
        if (active) setError(e.message);
      },
    );
    return () => {
      active = false;
    };
  }, []);
  const summarize = useCallback(
    async (override?: {
      start: number;
      end: number;
      question: string;
      asOf?: number;
    }) => {
      setBusy(true);
      setError('');
      setNotice('');
      if (override) {
        setStart(formatTime(override.start));
        setEnd(formatTime(override.end));
        setCutoff(formatTime(override.asOf ?? override.end));
        setQuestion(override.question);
      }
      try {
        const data = await api('recap', {
          sourceId,
          start: override?.start ?? parseTime(start),
          end: override?.end ?? parseTime(end),
          asOf: override?.asOf ?? parseTime(cutoff),
          question: override?.question ?? question,
          runner,
          injectFailure: retry,
        });
        setRun(data.run);
        await refresh();
        return data.run;
      } catch (e) {
        setError((e as Error).message);
        throw e;
      } finally {
        setBusy(false);
      }
    },
    [sourceId, start, end, cutoff, question, runner, retry, refresh],
  );
  useEffect(() => {
    const context = (
      document as unknown as {
        modelContext?: {
          registerTool: (
            tool: unknown,
            options: { signal: AbortSignal },
          ) => void;
        };
      }
    ).modelContext;
    if (!context) return;
    const controller = new AbortController();
    context.registerTool(
      {
        name: 'summarize_interval',
        description:
          'Create an extractive recap from the selected source in this browser session. Saves a run. Times are seconds from the video start.',
        inputSchema: {
          type: 'object',
          properties: {
            start: { type: 'number' },
            end: { type: 'number' },
            asOf: { type: 'number' },
            question: { type: 'string' },
          },
          required: ['start', 'end', 'asOf', 'question'],
        },
        execute: async (input: {
          start: number;
          end: number;
          asOf: number;
          question: string;
        }) => ({
          content: [
            { type: 'text', text: JSON.stringify(await summarize(input)) },
          ],
        }),
      },
      { signal: controller.signal },
    );
    return () => controller.abort();
  }, [summarize]);
  async function importSource() {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const body = append
        ? {
            appendTo: sourceId,
            revision: source?.revision,
            availableEnd: parseTime(coverage),
            format,
            text,
          }
        : {
            source: {
              title,
              url,
              kind,
              duration: parseTime(duration),
              availableStart: parseTime(coverageStart),
              availableEnd: parseTime(coverage),
            },
            format,
            text,
          };
      const data = await api('sources', body);
      await refresh();
      setSourceId(data.source.id);
      setStart(formatTime(data.source.availableStart));
      setEnd(formatTime(data.source.availableEnd));
      setCutoff(formatTime(data.source.availableEnd));
      setRun(null);
      setNotice(
        append
          ? 'Live evidence appended. New requests use the updated revision.'
          : 'Evidence imported. Open Recap to ask about this source.',
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function review(decision: string) {
    if (!run) return;
    try {
      const data = await api('review', { id: run.id, decision });
      setRun(data.run);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  function download() {
    if (!run) return;
    const a = document.createElement('a');
    const link = URL.createObjectURL(
      new Blob([JSON.stringify(run, null, 2)], { type: 'application/json' }),
    );
    a.href = link;
    a.download = `racetime-${run.id}.json`;
    a.click();
    URL.revokeObjectURL(link);
  }
  return (
    <main className="workspace">
      <header className="mast">
        <strong>
          RACE<span>TIME</span> COPILOT
        </strong>
        <span>Catch up. Check the evidence. Rejoin the race.</span>
        <a
          href="https://github.com/sivalinb/racetime-copilot"
          target="_blank"
          rel="noreferrer"
        >
          GitHub ↗
        </a>
      </header>
      <section className="intro">
        <div>
          <p className="eyebrow">A RACE STORY, ON YOUR CLOCK</p>
          <h1>
            Pick a moment.
            <br />
            Get the whole story.
          </h1>
          <p>
            Ask about any available interval. Follow runners, inspect
            conflicting reports, and catch up without jumping ahead.
          </p>
        </div>
        <img
          className="hero-art"
          src="/art/overview.png"
          alt="A race viewer selects a time window and receives an evidence-linked recap"
        />
      </section>
      <div className="mode-note">
        <strong>Evidence mode</strong> · Import transcripts or timestamped
        observations. Direct video understanding with Gemini is a future
        connection. The demo is entirely fictional.
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && <output className="notice">{notice}</output>}
      <Tabs defaultValue="recap">
        <TabsList>
          <TabsTrigger value="recap">Recap</TabsTrigger>
          <TabsTrigger value="import">Import / live append</TabsTrigger>
          <TabsTrigger value="history">History & traces</TabsTrigger>
          <TabsTrigger value="about">How it works</TabsTrigger>
        </TabsList>
        <TabsContent value="recap">
          <div className="desk">
            <section className="panel">
              <h2>01 / Choose your window</h2>
              <label>
                Evidence source
                <select
                  value={sourceId}
                  onChange={(e) => {
                    const s = sources.find((s) => s.id === e.target.value)!;
                    setSourceId(s.id);
                    setStart(formatTime(s.availableStart));
                    setEnd(
                      formatTime(
                        Math.min(s.availableEnd, s.availableStart + 900),
                      ),
                    );
                    setCutoff(
                      formatTime(
                        Math.min(s.availableEnd, s.availableStart + 900),
                      ),
                    );
                    setRun(null);
                    setSeek(0);
                  }}
                >
                  {sources.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.title}
                    </option>
                  ))}
                </select>
              </label>
              {source && (
                <p className="small">
                  {source.kind === 'live'
                    ? 'Live evidence replay'
                    : 'Recorded evidence'}{' '}
                  · {formatTime(source.availableStart)}–
                  {formatTime(source.availableEnd)} available · Revision{' '}
                  {source.revision}
                </p>
              )}
              {source?.url ? (
                <iframe
                  title="Selected race video"
                  className="video"
                  src={`https://www.youtube.com/embed/${youtubeId(source.url)}?start=${seek}`}
                  allowFullScreen
                />
              ) : (
                <div className="demo-card">
                  {source?.provenance === 'fictional_demo' ? (
                    <>
                      <span className="pill">FICTIONAL REPLAY</span>
                      <p>
                        Canyon Relay
                        <br />
                        <strong>Two reports. One uncertain lead.</strong>
                      </p>
                      <small>
                        Try the first 15 minutes, then inspect the conflicting
                        ridge reports.
                      </small>
                    </>
                  ) : (
                    <>
                      <span className="pill">IMPORTED EVIDENCE</span>
                      <p>
                        <strong>{source?.title || 'Loading source…'}</strong>
                      </p>
                      <small>
                        Timestamped observations are available. This source has
                        no linked video.
                      </small>
                    </>
                  )}
                </div>
              )}
              <div className="range">
                <label>
                  Start
                  <Input
                    value={start}
                    onChange={(e) => setStart(e.target.value)}
                  />
                </label>
                <label>
                  End
                  <Input
                    value={end}
                    onChange={(e) => {
                      setEnd(e.target.value);
                      setCutoff(e.target.value);
                    }}
                  />
                </label>
              </div>
              <label>
                Spoiler cutoff (as of)
                <Input
                  value={cutoff}
                  onChange={(e) => setCutoff(e.target.value)}
                />
              </label>
              <p className="small">
                Times use video elapsed time: seconds, MM:SS or HH:MM:SS.
              </p>
              <label>
                Your question
                <Input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                />
              </label>
              <label>
                Runner filter (optional)
                <Input
                  placeholder="e.g. Maya Chen"
                  value={runner}
                  onChange={(e) => setRunner(e.target.value)}
                />
              </label>
              <Button
                disabled={busy || !source}
                onClick={() => {
                  summarize().catch(() => {});
                }}
              >
                {busy ? 'Checking the evidence…' : 'Create my recap →'}
              </Button>
              <details>
                <summary>Test a recovery path</summary>
                <label className="check">
                  <input
                    type="checkbox"
                    checked={retry}
                    onChange={(e) => setRetry(e.target.checked)}
                  />
                  Simulate one retrieval failure
                </label>
              </details>
            </section>
            <section className="panel recap" aria-live="polite">
              <h2>02 / Follow the evidence</h2>
              {!run ? (
                <div className="empty">
                  <img
                    src="/art/workflow.png"
                    alt="Select an interval, collect evidence, and review the recap"
                  />
                  <h3>Your catch-up starts here.</h3>
                  <p>
                    Each finding includes its source timestamp. Conflicting
                    claims stay visible so you can decide what needs a second
                    look.
                  </p>
                </div>
              ) : (
                <>
                  <div className="result-head">
                    <span
                      className={`pill ${run.status === 'needs_review' ? 'amber' : ''}`}
                    >
                      {run.status.replaceAll('_', ' ').toUpperCase()}
                    </span>
                    <span className="small">
                      {run.latencyMs.toFixed(0)} ms ·{' '}
                      {run.cacheHit ? 'cache hit' : 'fresh run'}
                    </span>
                  </div>
                  <h3>
                    {formatTime(run.start)}–{formatTime(run.end)}
                  </h3>
                  {run.warnings.map((w) => (
                    <p className="warning" key={w}>
                      {w}
                    </p>
                  ))}
                  {run.conflicts.map((c) => (
                    <div className="conflict" key={c.key}>
                      <strong>Reports disagree</strong>
                      <p>
                        {c.values.join(' / ')} · {c.ids.join(', ')}
                      </p>
                    </div>
                  ))}
                  <ol className="findings">
                    {run.findings.map((f) => (
                      <li key={f.id}>
                        <div>
                          {f.url ? (
                            <button
                              className="time"
                              onClick={() => setSeek(Math.floor(f.start))}
                            >
                              {formatTime(f.start)}
                            </button>
                          ) : (
                            <span className="small">{formatTime(f.start)}</span>
                          )}
                          <span className="small">
                            {f.kind} · {f.id}
                          </span>
                        </div>
                        <p>{f.text}</p>
                        {f.url && (
                          <a href={f.url} target="_blank" rel="noreferrer">
                            Open source at timestamp ↗
                          </a>
                        )}
                      </li>
                    ))}
                  </ol>
                  <div className="review">
                    <p>
                      <strong>Human review:</strong> {run.review}
                    </p>
                    <Button onClick={() => review('approved')}>
                      Approve recap
                    </Button>
                    <Button onClick={() => review('rejected')}>
                      Reject recap
                    </Button>
                    <Button onClick={download}>Export JSON</Button>
                  </div>
                  <details>
                    <summary>Inspect this run’s trace</summary>
                    {run.trace.map((t, i) => (
                      <p key={i}>
                        <strong>
                          {t.name} · {t.status}
                        </strong>
                        <br />
                        {t.detail}
                      </p>
                    ))}
                  </details>
                </>
              )}
            </section>
          </div>
        </TabsContent>
        <TabsContent value="import">
          <div className="desk">
            <section className="panel">
              <h2>Bring your race evidence</h2>
              <p>
                Import VTT/SRT captions or JSON observations you are allowed to
                use. A YouTube URL links evidence to playback; the URL alone
                does not analyze the video.
              </p>
              <label className="check">
                <input
                  type="checkbox"
                  checked={append}
                  onChange={(e) => setAppend(e.target.checked)}
                />
                Append to selected live source
              </label>
              {append ? (
                <p>
                  Selected: {source?.title}. Select an imported live source in
                  Recap first. Evidence IDs must be new.
                </p>
              ) : (
                <>
                  <label>
                    Title
                    <Input
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                    />
                  </label>
                  <label>
                    YouTube video URL (optional)
                    <Input
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://www.youtube.com/watch?v=…"
                    />
                  </label>
                  <label>
                    Source type
                    <select
                      value={kind}
                      onChange={(e) => setKind(e.target.value)}
                    >
                      <option value="recorded">Recorded</option>
                      <option value="live">Live / appendable evidence</option>
                    </select>
                  </label>
                  <label>
                    Total duration or maximum live horizon
                    <Input
                      value={duration}
                      onChange={(e) => setDuration(e.target.value)}
                    />
                  </label>
                  <label>
                    Available start
                    <Input
                      value={coverageStart}
                      onChange={(e) => setCoverageStart(e.target.value)}
                    />
                  </label>
                </>
              )}
              <label>
                Available end
                <Input
                  value={coverage}
                  onChange={(e) => setCoverage(e.target.value)}
                />
              </label>
              <label>
                Format
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                >
                  <option value="vtt">WebVTT</option>
                  <option value="srt">SRT</option>
                  <option value="json">JSON observations</option>
                </select>
              </label>
              <label>
                Choose transcript file
                <Input
                  type="file"
                  accept=".vtt,.srt,.json,.txt"
                  onChange={async (e) => {
                    const f = e.target.files?.[0];
                    if (f) {
                      if (f.size > 1500000) {
                        setError('File exceeds 1.5 MB.');
                        return;
                      }
                      setText(await f.text());
                      const ext = f.name.split('.').at(-1);
                      if (['vtt', 'srt', 'json'].includes(ext || ''))
                        setFormat(ext!);
                    }
                  }}
                />
              </label>
              <label>
                Or paste evidence
                <Textarea
                  rows={9}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={
                    'WEBVTT\n\n00:00:10.000 --> 00:00:20.000\nCommentary describes the checkpoint.'
                  }
                />
              </label>
              <Button disabled={busy || !text} onClick={importSource}>
                {busy
                  ? 'Importing…'
                  : append
                    ? 'Append observations'
                    : 'Import source'}
              </Button>
            </section>
            <section className="panel">
              <h2>Designed for honest catch-up</h2>
              <img
                className="wide-art"
                src="/art/audience.png"
                alt="Race fans, crews, and organizers use the same evidence timeline"
              />
              <h3>Control what is available</h3>
              <p>
                Coverage describes the imported portion. Gaps can still exist
                within it. Each cue must fit inside the declared coverage.
                Recaps only use fully contained cues available before the
                spoiler cutoff.
              </p>
              <h3>Bring structured context</h3>
              <p>
                JSON fields: id, start, end, text, kind. Optional runner,
                claimKey, claimValue, and availableAt support runner filtering
                and explicit contradictory claims. Times are elapsed seconds.
              </p>
              <h3>Live today, automated later</h3>
              <p>
                Live mode accepts additional timestamped observations and
                increments the source revision. It does not connect to or
                continuously watch a live YouTube feed.
              </p>
            </section>
          </div>
        </TabsContent>
        <TabsContent value="history">
          <section className="panel">
            <h2>Recent runs in this browser</h2>
            <p>
              Imports and the most recent 100 runs persist in local D1 storage;
              the latest 20 appear here. Clearing the session cookie makes them
              inaccessible from this browser.
            </p>
            {runs.length === 0 ? (
              <p>No runs yet. Create a recap to see its trace.</p>
            ) : (
              runs.map((r) => (
                <details key={r.id}>
                  <summary>
                    {r.sourceTitle} · {formatTime(r.start)}–{formatTime(r.end)}{' '}
                    · {r.review} · {r.latencyMs.toFixed(0)} ms
                  </summary>
                  <p>
                    {r.question} · revision {r.sourceRevision} ·{' '}
                    {r.findings.length} findings ·{' '}
                    {r.cacheHit ? 'cached' : 'uncached'}
                  </p>
                  {r.trace.map((t, i) => (
                    <p key={i}>
                      <strong>
                        {t.name} / {t.status}
                      </strong>{' '}
                      — {t.detail}
                    </p>
                  ))}
                  <Button
                    onClick={() => {
                      setRun(r);
                      setSourceId(r.sourceId);
                      setStart(formatTime(r.start));
                      setEnd(formatTime(r.end));
                      setCutoff(formatTime(r.asOf));
                      setQuestion(r.question);
                      setNotice(
                        'Run selected. Open Recap to review or export it.',
                      );
                    }}
                  >
                    Load saved recap
                  </Button>
                </details>
              ))
            )}
          </section>
        </TabsContent>
        <TabsContent value="about">
          <section className="panel">
            <h2>A capstone built around race-day questions</h2>
            <p>
              RaceTime connects endurance-racing experience with observability
              and evidence-driven system design.
            </p>
            <img
              className="wide-art"
              src="/art/workflow.png"
              alt="RaceTime evidence workflow"
            />
            <div className="about-grid">
              <div>
                <h3>1. A usable product</h3>
                <p>
                  React and TypeScript build the workbench. D1 stores sources,
                  observations, runs, and human decisions.
                </p>
              </div>
              <div>
                <h3>2. Grounded retrieval</h3>
                <p>
                  Validated transcript ingestion, time-bounded chunks,
                  BM25-style lexical scores, and deterministic hashed vectors
                  retrieve evidence. These vectors are not learned semantic
                  embeddings.
                </p>
              </div>
              <div>
                <h3>3. Stateful orchestration</h3>
                <p>
                  LangGraph routes, retrieves, retries a failed tool once,
                  verifies conflicting claims, and produces an extractive recap
                  with a persistent human review decision.
                </p>
              </div>
              <div>
                <h3>4. Observable quality</h3>
                <p>
                  Per-run traces, latency, cache hits, and a reproducible
                  evaluation suite make failure cases inspectable. LangSmith
                  export can be configured separately.
                </p>
              </div>
              <div>
                <h3>5. Specialization lab</h3>
                <p>
                  The repository includes a separate LoRA intent-routing
                  experiment. Its held-out evaluation determines whether a
                  learned router earns a place in the product.
                </p>
              </div>
              <div>
                <h3>Next: video understanding</h3>
                <p>
                  Gemini is deferred. Future work adds bounded multimodal
                  observations, official timing feeds, and live ingestion with
                  explicit coverage tracking.
                </p>
              </div>
            </div>
          </section>
        </TabsContent>
      </Tabs>
      <footer>
        RaceTime Copilot · Prototype · Evidence reports are not official race
        results.
      </footer>
    </main>
  );
}
