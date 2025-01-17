-- Current sql file was generated after introspecting the database
-- If you want to run this migration please uncomment this code before executing migrations
/*
CREATE TABLE "artists" (
	"apple_music" text DEFAULT '',
	"artist_photos" json DEFAULT '[]'::json,
	"bandcamp" text DEFAULT '',
	"bandsintown" text DEFAULT '',
	"biography" text DEFAULT '',
	"birthdate" text DEFAULT '',
	"city" text DEFAULT '',
	"created" text DEFAULT '',
	"email" text DEFAULT '',
	"facebook" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"instagram" text DEFAULT '',
	"legal_name" text DEFAULT '',
	"linkedin" text DEFAULT '',
	"mixcloud" text DEFAULT '',
	"phone" text DEFAULT '',
	"slug" text DEFAULT '',
	"snapchat" text DEFAULT '',
	"songkick" text DEFAULT '',
	"soundcloud" text DEFAULT '',
	"spotify" text DEFAULT '',
	"stage_name" text DEFAULT '',
	"tiktok" text DEFAULT '',
	"twitch" text DEFAULT '',
	"updated" text DEFAULT '',
	"website" text DEFAULT '',
	"x" text DEFAULT '',
	"youtube" text DEFAULT '',
	"country" text DEFAULT '',
	"anr" text DEFAULT '',
	"is_signed" boolean DEFAULT false,
	"org_id" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "labels" (
	"created" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"name" text DEFAULT '',
	"updated" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "genres" (
	"created" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"name" text DEFAULT '',
	"updated" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "subgenres" (
	"created" text DEFAULT '',
	"genre" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"name" text DEFAULT '',
	"updated" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "releases" (
	"catalog_number" text DEFAULT '',
	"created" text DEFAULT '',
	"genre" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"is_compilation" boolean DEFAULT false,
	"label" text DEFAULT '',
	"release_date" text DEFAULT '',
	"subgenre" text DEFAULT '',
	"release_title" text DEFAULT '',
	"upc_code" text DEFAULT '',
	"updated" text DEFAULT '',
	"release_version" text DEFAULT '',
	"contracts" json DEFAULT '[]'::json,
	"media_assets" json DEFAULT '[]'::json,
	"language" text DEFAULT '',
	"tracks" json DEFAULT '[]'::json,
	"slug" text DEFAULT '',
	"cover_artwork" json DEFAULT '[]'::json,
	"description" text DEFAULT '',
	"bandcamp" text DEFAULT '',
	"vinyl" text DEFAULT '',
	"org_id" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "languages" (
	"created" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"name" text DEFAULT '',
	"updated" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "countries" (
	"created" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"name" text DEFAULT '',
	"updated" text DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE "tracks" (
	"audio_file" text DEFAULT '',
	"created" text DEFAULT '',
	"demo_files" json DEFAULT '[]'::json,
	"explicit_status" text DEFAULT '',
	"genre" text DEFAULT '',
	"id" text PRIMARY KEY DEFAULT '''r''||lower(hex(randomblob(7)))' NOT NULL,
	"mix_version" text DEFAULT '',
	"recording_location" text DEFAULT '',
	"subgenre" text DEFAULT '',
	"track_title" text DEFAULT '',
	"updated" text DEFAULT '',
	"recording_year" text DEFAULT '',
	"isrc_code" text DEFAULT '',
	"lyrics" text DEFAULT '',
	"lyrics_text" text DEFAULT '',
	"primary_artists" json DEFAULT '[]'::json,
	"featuring_artists" json DEFAULT '[]'::json,
	"remix_artists" json DEFAULT '[]'::json,
	"writer_artists" json DEFAULT '[]'::json,
	"performer_artists" json DEFAULT '[]'::json,
	"engineer_artists" json DEFAULT '[]'::json
);

*/