/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import type { artists, releases, tracks } from '$lib/db/schema';

export type Artist = typeof artists.$inferSelect;
export type Release = typeof releases.$inferSelect;
export type Track = typeof tracks.$inferSelect;

export type NewArtist = typeof artists.$inferInsert;
export type NewRelease = typeof releases.$inferInsert;
export type NewTrack = typeof tracks.$inferInsert;
