import { sqliteTable, text, integer, index } from 'drizzle-orm/sqlite-core';
export const sources = sqliteTable(
  'sources',
  {
    id: text('id').primaryKey(),
    session: text('session').notNull(),
    payload: text('payload').notNull(),
    revision: integer('revision').notNull().default(1),
  },
  (t) => [index('idx_sources_session').on(t.session)],
);
export const evidence = sqliteTable(
  'evidence',
  {
    id: text('id').primaryKey(),
    session: text('session').notNull(),
    sourceId: text('source_id').notNull(),
    start: integer('start').notNull(),
    end: integer('end').notNull(),
    payload: text('payload').notNull(),
  },
  (t) => [index('idx_evidence_source_time').on(t.session, t.sourceId, t.start)],
);
export const runs = sqliteTable(
  'runs',
  {
    id: text('id').primaryKey(),
    session: text('session').notNull(),
    sourceId: text('source_id').notNull(),
    createdAt: text('created_at').notNull(),
    payload: text('payload').notNull(),
  },
  (t) => [index('idx_runs_session_created').on(t.session, t.createdAt)],
);
