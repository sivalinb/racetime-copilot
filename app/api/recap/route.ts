import { querySchema } from '../../../lib/contracts';
import { session, response, loadSource, saveRun } from '../../../lib/store';
import { runRecap } from '../../../lib/workflow';
export async function POST(req: Request) {
  const s = session(req);
  try {
    const raw = await req.text();
    if (raw.length > 5000) throw new Error('Request too large.');
    const q = querySchema.parse(JSON.parse(raw));
    const { source, events } = await loadSource(s.id, q.sourceId);
    const run = await runRecap(source, events, q);
    await saveRun(s.id, run);
    return response({ run }, s);
  } catch (e) {
    return response(
      { error: e instanceof Error ? e.message : 'Recap failed.' },
      s,
      400,
    );
  }
}
