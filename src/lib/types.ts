import type { artists, releases, tracks } from '$lib/db/schema';

export type Artist = typeof artists.$inferSelect;
export type Release = typeof releases.$inferSelect;
export type Track = typeof tracks.$inferSelect;

export type NewArtist = typeof artists.$inferInsert;
export type NewRelease = typeof releases.$inferInsert;
export type NewTrack = typeof tracks.$inferInsert;
