import { session, response, listSources, history } from '../../../lib/store';
export async function GET(req: Request) {
  const s = session(req);
  try {
    return response(
      {
        sources: await listSources(s.id),
        history: await history(s.id),
        capabilities: {
          mode: 'extractive',
          gemini: false,
          live: 'import-and-append',
          storage: 'D1',
          router: 'rules',
        },
      },
      s,
    );
  } catch {
    return response(
      { error: 'Storage is unavailable. Check the local server logs.' },
      s,
      503,
    );
  }
}
