import { pgTable, text, json, boolean, uniqueIndex, uuid, timestamp, date } from 'https://esm.sh/drizzle-orm@0.29.3/pg-core';
import { sql } from 'https://esm.sh/drizzle-orm@0.29.3';

export const artists = pgTable(
  'artists',
  {
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
  },
  (table) => ({
    orgIdIdx: uniqueIndex('artists_org_id_idx').on(table.orgId),
  })
); 