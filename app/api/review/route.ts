import { z } from 'zod';
import { session, response, reviewRun } from '../../../lib/store';
export async function POST(req: Request) {
  const s = session(req);
  try {
    const { id, decision } = z
      .object({
        id: z.string().max(100),
        decision: z.enum(['approved', 'rejected']),
      })
      .parse(await req.json());
    return response({ run: await reviewRun(s.id, id, decision) }, s);
  } catch (e) {
    return response(
      { error: e instanceof Error ? e.message : 'Review failed.' },
      s,
      400,
    );
  }
}
