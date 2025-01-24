import { pgTable, text, json, boolean, uuid, timestamp, date } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const artists = pgTable('artists', {
  appleMusic: text('apple_music').default(''),
  artistPhotos: json('artist_photos').default([]),
  bandcamp: text().default(''),
  bandsintown: text().default(''),
  biography: text().default(''),
  birthdate: date('birthdate'),
  city: text().default(''),
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  email: text().default(''),
  facebook: text().default(''),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  instagram: text().default(''),
  legalName: text('legal_name').default(''),
  linkedin: text().default(''),
  mixcloud: text().default(''),
  phone: text().default(''),
  slug: text().default(''),
  snapchat: text().default(''),
  songkick: text().default(''),
  soundcloud: text().default(''),
  spotify: text().default(''),
  stageName: text('stage_name').default(''),
  tiktok: text().default(''),
  twitch: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
  website: text().default(''),
  x: text().default(''),
  youtube: text().default(''),
  country: text().default(''),
  anr: text().default(''),
  isSigned: boolean('is_signed').default(false),
  orgId: text('org_id').default(''),
  soundchartsId: text('soundcharts_id').default(''),
  metadata: json('metadata').default({}),
  streaming: json('streaming').default({}),
  followers: json('followers').default({}),
});

export const labels = pgTable('labels', {
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  name: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
});

export const genres = pgTable('genres', {
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  name: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
});

export const subgenres = pgTable('subgenres', {
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  genre: text().default(''),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  name: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
});

export const releases = pgTable('releases', {
  catalogNumber: text('catalog_number').default(''),
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  genre: text().default(''),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  isCompilation: boolean('is_compilation').default(false),
  label: text().default(''),
  releaseDate: date('release_date'),
  subgenre: text().default(''),
  releaseTitle: text('release_title').default(''),
  upcCode: text('upc_code').default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
  releaseVersion: text('release_version').default(''),
  contracts: json().default([]),
  mediaAssets: json('media_assets').default([]),
  language: text().default(''),
  tracks: json().default([]),
  slug: text().default(''),
  coverArtwork: json('cover_artwork').default([]),
  description: text().default(''),
  bandcamp: text().default(''),
  vinyl: text().default(''),
  orgId: text('org_id').default(''),
  labelId: uuid('label_id').references(() => labels.id),
  genreId: uuid('genre_id').references(() => genres.id),
  subgenreId: uuid('subgenre_id').references(() => subgenres.id),
});

export const languages = pgTable('languages', {
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  name: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
});

export const countries = pgTable('countries', {
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  name: text().default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
});

export const tracks = pgTable('tracks', {
  audioFile: text('audio_file').default(''),
  created: timestamp('created', { withTimezone: true }).defaultNow().notNull(),
  demoFiles: json('demo_files').default([]),
  explicitStatus: text('explicit_status').default(''),
  genre: text().default(''),
  id: uuid('id')
    .default(sql`uuid_generate_v4()`)
    .notNull()
    .primaryKey(),
  mixVersion: text('mix_version').default(''),
  recordingLocation: text('recording_location').default(''),
  subgenre: text().default(''),
  trackTitle: text('track_title').default(''),
  updated: timestamp('updated', { withTimezone: true }).defaultNow().notNull(),
  recordingYear: text('recording_year').default(''),
  isrcCode: text('isrc_code').default(''),
  lyrics: text().default(''),
  lyricsText: text('lyrics_text').default(''),
  primaryArtists: json('primary_artists').default([]),
  featuringArtists: json('featuring_artists').default([]),
  remixArtists: json('remix_artists').default([]),
  writerArtists: json('writer_artists').default([]),
  performerArtists: json('performer_artists').default([]),
  engineerArtists: json('engineer_artists').default([]),
});
