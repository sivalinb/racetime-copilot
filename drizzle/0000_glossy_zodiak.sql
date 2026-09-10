CREATE TABLE `evidence` (
	`id` text PRIMARY KEY NOT NULL,
	`session` text NOT NULL,
	`source_id` text NOT NULL,
	`start` integer NOT NULL,
	`end` integer NOT NULL,
	`payload` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_evidence_source_time` ON `evidence` (`session`,`source_id`,`start`);--> statement-breakpoint
CREATE TABLE `runs` (
	`id` text PRIMARY KEY NOT NULL,
	`session` text NOT NULL,
	`source_id` text NOT NULL,
	`created_at` text NOT NULL,
	`payload` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_runs_session_created` ON `runs` (`session`,`created_at`);--> statement-breakpoint
CREATE TABLE `sources` (
	`id` text PRIMARY KEY NOT NULL,
	`session` text NOT NULL,
	`payload` text NOT NULL,
	`revision` integer DEFAULT 1 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_sources_session` ON `sources` (`session`);