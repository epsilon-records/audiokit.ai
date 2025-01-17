import { pgTable, text, json, boolean } from "drizzle-orm/pg-core"
import { sql } from "drizzle-orm"



export const artists = pgTable("artists", {
	appleMusic: text("apple_music").default('),
	artistPhotos: json("artist_photos").default([]),
	bandcamp: text().default('),
	bandsintown: text().default('),
	biography: text().default('),
	birthdate: text().default('),
	city: text().default('),
	created: text().default('),
	email: text().default('),
	facebook: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	instagram: text().default('),
	legalName: text("legal_name").default('),
	linkedin: text().default('),
	mixcloud: text().default('),
	phone: text().default('),
	slug: text().default('),
	snapchat: text().default('),
	songkick: text().default('),
	soundcloud: text().default('),
	spotify: text().default('),
	stageName: text("stage_name").default('),
	tiktok: text().default('),
	twitch: text().default('),
	updated: text().default('),
	website: text().default('),
	x: text().default('),
	youtube: text().default('),
	country: text().default('),
	anr: text().default('),
	isSigned: boolean("is_signed").default(false),
	orgId: text("org_id").default('),
});

export const labels = pgTable("labels", {
	created: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	name: text().default('),
	updated: text().default('),
});

export const genres = pgTable("genres", {
	created: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	name: text().default('),
	updated: text().default('),
});

export const subgenres = pgTable("subgenres", {
	created: text().default('),
	genre: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	name: text().default('),
	updated: text().default('),
});

export const releases = pgTable("releases", {
	catalogNumber: text("catalog_number").default('),
	created: text().default('),
	genre: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	isCompilation: boolean("is_compilation").default(false),
	label: text().default('),
	releaseDate: text("release_date").default('),
	subgenre: text().default('),
	releaseTitle: text("release_title").default('),
	upcCode: text("upc_code").default('),
	updated: text().default('),
	releaseVersion: text("release_version").default('),
	contracts: json().default([]),
	mediaAssets: json("media_assets").default([]),
	language: text().default('),
	tracks: json().default([]),
	slug: text().default('),
	coverArtwork: json("cover_artwork").default([]),
	description: text().default('),
	bandcamp: text().default('),
	vinyl: text().default('),
	orgId: text("org_id").default('),
});

export const languages = pgTable("languages", {
	created: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	name: text().default('),
	updated: text().default('),
});

export const countries = pgTable("countries", {
	created: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	name: text().default('),
	updated: text().default('),
});

export const tracks = pgTable("tracks", {
	audioFile: text("audio_file").default('),
	created: text().default('),
	demoFiles: json("demo_files").default([]),
	explicitStatus: text("explicit_status").default('),
	genre: text().default('),
	id: text().default('\'r\'||lower(hex(randomblob(7)))').primaryKey().notNull(),
	mixVersion: text("mix_version").default('),
	recordingLocation: text("recording_location").default('),
	subgenre: text().default('),
	trackTitle: text("track_title").default('),
	updated: text().default('),
	recordingYear: text("recording_year").default('),
	isrcCode: text("isrc_code").default('),
	lyrics: text().default('),
	lyricsText: text("lyrics_text").default('),
	primaryArtists: json("primary_artists").default([]),
	featuringArtists: json("featuring_artists").default([]),
	remixArtists: json("remix_artists").default([]),
	writerArtists: json("writer_artists").default([]),
	performerArtists: json("performer_artists").default([]),
	engineerArtists: json("engineer_artists").default([]),
});
