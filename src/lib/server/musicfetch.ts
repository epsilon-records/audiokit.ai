import { MUSICFETCH_TOKEN } from '$env/static/private';
import { debug } from '$lib/utils/logger';

export async function getMusicfetchData(spotifyUrl: string, services: string[]) {
  const requestId = crypto.randomUUID();

  try {
    const response: Response = await fetch(
      `https://api.musicfetch.io/url?url=${encodeURIComponent(spotifyUrl)}&services=${services.join(',')}`,
      {
        headers: {
          'x-musicfetch-token': MUSICFETCH_TOKEN,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Musicfetch request failed with status ${response.status}`);
    }

    const data = await response.json();
    return data.result.services;
  } catch (error) {
    debug({
      requestId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Error fetching Musicfetch data',
    });
    throw error;
  }
}
