// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Import Supabase client
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7';

// Import soundcharts
import { soundcharts } from "./soundcharts.ts";

// Types
interface Artist {
  id: string
  spotify: string | null
  metadata: Record<string, unknown> | null
  streaming: Record<string, unknown> | null
  followers: Record<string, unknown> | null
  updated: string | null
}

interface ArtistUpdate {
  artistId: string
  success: boolean
  error?: string
}

// Environment configuration
function initSupabase() {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

  if (!supabaseUrl) throw new Error('SUPABASE_URL is required')
  if (!supabaseKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY is required')

  return createClient(supabaseUrl, supabaseKey)
}

// Extract Spotify ID from URL
function extractSpotifyId(spotifyUrl: string): string | null {
  try {
    const id = spotifyUrl.split('/').pop()
    return id || null
  } catch {
    return null
  }
}

// Fetch artist data from Soundcharts
async function fetchSoundchartsData(spotifyUrl: string) {
  try {
    const spotifyId = extractSpotifyId(spotifyUrl)
    if (!spotifyId) {
      throw new Error('Invalid Spotify URL')
    }
    return await soundcharts.getArtistStats(spotifyId)
  } catch (error) {
    console.error('Error fetching Soundcharts data:', error)
    return null
  }
}

// Update single artist
async function updateArtist(supabase: ReturnType<typeof createClient>, artist: Artist): Promise<ArtistUpdate> {
  try {
    if (!artist.spotify) {
      return { artistId: artist.id, success: false, error: 'No Spotify URL' }
    }

    const soundchartsData = await fetchSoundchartsData(artist.spotify)
    if (!soundchartsData) {
      return { artistId: artist.id, success: false, error: 'No Soundcharts data available' }
    }

    const { error } = await supabase
      .from('artists')
      .update({
        metadata: soundchartsData.metadata,
        streaming: soundchartsData.streaming,
        followers: soundchartsData.followers,
        updated: new Date().toISOString(),
      })
      .eq('id', artist.id)

    if (error) throw error

    return { artistId: artist.id, success: true }
  } catch (error) {
    return { 
      artistId: artist.id, 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

// Main handler
Deno.serve(async (req: Request) => {
  try {
    console.log('Starting soundcharts enrichment function')
    const supabase = initSupabase()

    // Fetch artists with Spotify URLs
    const { data: artists, error: fetchError } = await supabase
      .from('artists')
      .select('*')
      .not('spotify', 'eq', '')

    if (fetchError) throw fetchError

    if (!artists?.length) {
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: 'No artists found to update',
          updates: []
        }), 
        { headers: { 'Content-Type': 'application/json' } }
      )
    }

    console.log(`Found ${artists.length} artists to update`)

    // Process updates
    const updates = await Promise.all(
      artists.map((artist) => updateArtist(supabase, artist))
    )

    return new Response(
      JSON.stringify({ success: true, updates }), 
      { headers: { 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error in soundcharts enrichment:', error)
    
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
})

/* To invoke locally:
  1. Run `supabase start`
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/soundcharts-enrichment' \
    --header 'Authorization: Bearer ' \
    --header 'Content-Type: application/json'
*/
