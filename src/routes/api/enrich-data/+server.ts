import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/server/soundcharts';
import { error } from '@sveltejs/kit';
import { eq, not, or } from 'drizzle-orm';

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
    let soundchartsId = artist.soundchartsId;

    // If no soundchartsId but has spotify URL, try to get soundchartsId
    if (!soundchartsId && artist.spotify) {
      const spotifyId = extractSpotifyId(artist.spotify);
      if (spotifyId) {
        soundchartsId = await soundcharts.getArtistIdFromSpotify(spotifyId);
        if (soundchartsId) {
          // Update artist with new soundchartsId
          await db.update(artists).set({ soundchartsId }).where(eq(artists.id, artist.id));
        }
      }
    }

    // If still no soundchartsId, return error
    if (!soundchartsId) {
      return {
        artistId: artist.id,
        success: false,
        error: 'No Soundcharts ID available',
      };
    }

    const soundchartsData = await soundcharts.getArtistStats(soundchartsId);
    if (!soundchartsData) {
      return {
        artistId: artist.id,
        success: false,
        error: 'No Soundcharts data available',
      };
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

    // Fetch artists with either Spotify URL or soundchartsId
    const artistData = await db
      .select()
      .from(artists)
      .where(or(not(eq(artists.spotify, '')), not(eq(artists.soundchartsId, ''))));

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

    return new Response(JSON.stringify({ success: true, updates }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    console.error('Error in soundcharts enrichment:', err);
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
