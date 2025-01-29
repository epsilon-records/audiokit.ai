import { db } from '../db/index.js';
import { artists } from '../db/schema.js';
import { eq, not, or, and } from 'drizzle-orm';
import logger from '../utils/logger.js';
import { enrichWithSoundcharts } from './enrichers/soundcharts.js';
import { enrichWithHubspot } from './enrichers/hubspot.js';
import { enrichWithMusicfetch } from './enrichers/musicfetch.js';

async function getArtistsToUpdate() {
  const soundchartsArtists = await db
    .select()
    .from(artists)
    .where(or(not(eq(artists.spotify, '')), not(eq(artists.soundchartsId, ''))));

  const musicfetchArtists = await db
    .select()
    .from(artists)
    .where(
      or(
        not(eq(artists.spotify, '')),
        not(eq(artists.appleMusic, '')),
        not(eq(artists.soundcloud, '')),
        not(eq(artists.youtube, ''))
      )
    );

  const hubspotArtists = await db
    .select()
    .from(artists)
    .where(
      and(
        not(eq(artists.email, '')),
        or(
          eq(artists.phone, ''),
          eq(artists.city, ''),
          eq(artists.country, ''),
          eq(artists.website, ''),
          eq(artists.spotify, ''),
          eq(artists.appleMusic, ''),
          eq(artists.soundcloud, ''),
          eq(artists.bandcamp, ''),
          eq(artists.facebook, ''),
          eq(artists.instagram, ''),
          eq(artists.mixcloud, ''),
          eq(artists.tiktok, ''),
          eq(artists.twitch, '')
        )
      )
    );

  return {
    soundchartsArtists,
    musicfetchArtists,
    hubspotArtists,
  };
}

export async function enrichData() {
  const requestId = crypto.randomUUID();
  logger.info({
    requestId,
    msg: 'Starting data enrichment process',
  });
  try {
    const { soundchartsArtists, musicfetchArtists, hubspotArtists } = await getArtistsToUpdate();
    const [soundchartsResults, musicfetchResults, hubspotResults] = await Promise.all([
      enrichWithSoundcharts(soundchartsArtists),
      enrichWithMusicfetch(musicfetchArtists),
      enrichWithHubspot(hubspotArtists),
    ]);
    return new Response(
      JSON.stringify({
        success: true,
        soundcharts: soundchartsResults,
        musicfetch: musicfetchResults,
        hubspot: hubspotResults,
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (err) {
    logger.info({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in data enrichment',
    });
  }
}
