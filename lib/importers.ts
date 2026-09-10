import { eventSchema, parseTime, type Evidence } from './contracts';
export function parseTranscript(
  text: string,
  format: 'vtt' | 'srt' | 'json',
): Evidence[] {
  if (new TextEncoder().encode(text).length > 1500000)
    throw new Error('Import limit is 1.5 MB.');
  if (format === 'json') {
    const raw = JSON.parse(text);
    const rows = Array.isArray(raw) ? raw : raw.events;
    if (!Array.isArray(rows))
      throw new Error('JSON must contain an events array.');
    if (rows.length > 5000) throw new Error('Maximum 5000 events per import.');
    return rows.map((e, i) =>
      eventSchema.parse({ ...e, id: e.id || `cue-${i + 1}` }),
    );
  }
  const blocks = text.replace(/\r/g, '').split(/\n\s*\n/);
  const result: Evidence[] = [];
  for (const block of blocks) {
    const lines = block.trim().split('\n');
    const at = lines.findIndex((l) => l.includes('-->'));
    if (at < 0) continue;
    const match = lines[at].match(/([\d:. ,]+)\s*-->\s*([\d:.,]+)/);
    if (!match) continue;
    const secs = (s: string) => {
      const [whole, fraction = '0'] = s.trim().replace(',', '.').split('.');
      return parseTime(whole) + Number('0.' + fraction);
    };
    const body = lines
      .slice(at + 1)
      .join(' ')
      .replace(/<[^>]*>/g, '')
      .trim();
    if (body)
      result.push(
        eventSchema.parse({
          id: `cue-${result.length + 1}`,
          start: secs(match[1]),
          end: secs(match[2]),
          text: body,
          kind: 'commentary',
        }),
      );
  }
  if (!result.length)
    throw new Error(
      'No timestamped cues found. Use VTT, SRT, or structured JSON.',
    );
  if (result.length > 5000) throw new Error('Maximum 5000 events per import.');
  return result;
}
