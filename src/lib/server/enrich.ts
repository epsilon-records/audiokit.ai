import { db } from '../db/index.js';
import { artists } from '../db/schema.js';
import { eq, not, or, and } from 'drizzle-orm';
import { logger } from '../utils/logger.js';
import { enrichWithSoundcharts } from './enrichers/soundcharts.js';
import { enrichWithHubspot } from './enrichers/hubspot.js';
import { enrichWithMusicfetch } from './enrichers/musicfetch.js';
import { serializeError } from 'serialize-error';

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
  const startTime = Date.now();

  logger.start(requestId, 'Starting data enrichment process', {
    metadata: {
      environment: process.env.NODE_ENV,
    },
  });

  try {
    const { soundchartsArtists, musicfetchArtists, hubspotArtists } = await getArtistsToUpdate();

    logger.process(requestId, 'Retrieved artists to update', {
      soundchartsCount: soundchartsArtists.length,
      musicfetchCount: musicfetchArtists.length,
      hubspotCount: hubspotArtists.length,
    });

    const [soundchartsResults, musicfetchResults, hubspotResults] = await Promise.all([
      enrichWithSoundcharts(soundchartsArtists),
      enrichWithMusicfetch(musicfetchArtists),
      enrichWithHubspot(hubspotArtists),
    ]);

    logger.success(requestId, 'Completed data enrichment process', {
      duration: Date.now() - startTime,
      results: {
        soundcharts: soundchartsResults.success,
        musicfetch: musicfetchResults.success,
        hubspot: hubspotResults.success,
      },
    });

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
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error in data enrichment process', serializedError, {
      duration: Date.now() - startTime,
    });

    return new Response(
      JSON.stringify({
        success: false,
        error: serializedError.message,
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
