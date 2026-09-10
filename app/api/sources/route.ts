import { sourceSchema, youtubeId } from '../../../lib/contracts';
import { parseTranscript } from '../../../lib/importers';
import {
  session,
  response,
  addSource,
  appendSource,
  validateEvents,
} from '../../../lib/store';
export async function POST(req: Request) {
  const s = session(req);
  try {
    const raw = await req.text();
    if (raw.length > 1600000) throw new Error('Import exceeds 1.6 MB.');
    const b = JSON.parse(raw);
    if (!['json', 'srt', 'vtt'].includes(b.format))
      throw new Error('Choose JSON, SRT or VTT.');
    const events = parseTranscript(b.text, b.format);
    if (b.appendTo) {
      if (!Number.isInteger(b.revision) || !Number.isFinite(b.availableEnd))
        throw new Error('Supply revision and availableEnd.');
      return response(
        {
          source: await appendSource(
            s.id,
            b.appendTo,
            b.revision,
            b.availableEnd,
            events,
          ),
        },
        s,
      );
    }
    const parsed = sourceSchema.parse({
      ...b.source,
      provenance: 'user_import',
    });
    if (parsed.url) youtubeId(parsed.url);
    const source = { ...parsed, id: crypto.randomUUID(), revision: 1 };
    validateEvents(source, events);
    await addSource(s.id, source, events);
    return response({ source }, s, 201);
  } catch (e) {
    return response(
      { error: e instanceof Error ? e.message : 'Import failed.' },
      s,
      400,
    );
  }
}
