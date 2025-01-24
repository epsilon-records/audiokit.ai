import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/server/soundcharts';
import { error } from '@sveltejs/kit';
import { eq, not } from 'drizzle-orm';

// Extract Spotify ID from URL
function extractSpotifyId(spotifyUrl: string): string | null {
  try {
    const id = spotifyUrl.split('/').pop();
    return id || null;
  } catch {
    return null;
  }
}

// Update single artist
async function updateArtist(artist: typeof artists.$inferSelect) {
  try {
    if (!artist.spotify) {
      return { artistId: artist.id, success: false, error: 'No Spotify URL' };
    }

    const spotifyId = extractSpotifyId(artist.spotify);
    if (!spotifyId) {
      return { artistId: artist.id, success: false, error: 'Invalid Spotify URL' };
    }

    const soundchartsData = await soundcharts.getArtistStats(spotifyId);
    if (!soundchartsData) {
      return { artistId: artist.id, success: false, error: 'No Soundcharts data available' };
    }

    await db
      .update(artists)
      .set({
        metadata: soundchartsData.metadata,
        streaming: soundchartsData.streaming,
        followers: soundchartsData.followers,
        updated: new Date(),
      })
      .where(eq(artists.id, artist.id));

    return { artistId: artist.id, success: true };
  } catch (error) {
    return {
      artistId: artist.id,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export async function GET() {
  try {
    console.log('Starting soundcharts enrichment cron');

    // Fetch artists with Spotify URLs
    const artistData = await db
      .select()
      .from(artists)
      .where(not(eq(artists.spotify, '')));

    if (!artistData.length) {
      return new Response(
        JSON.stringify({
          success: true,
          message: 'No artists found to update',
          updates: [],
        }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Found ${artistData.length} artists to update`);

    // Process updates
    const updates = await Promise.all(artistData.map((artist) => updateArtist(artist)));

    return new Response(
      JSON.stringify({ success: true, updates }),
      { headers: { 'Content-Type': 'application/json' } }
    );

  } catch (err) {
    console.error('Error in soundcharts enrichment:', err);
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}