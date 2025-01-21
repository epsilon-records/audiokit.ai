import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { eq } from 'drizzle-orm';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/server/soundcharts';
import { requireOrg } from '$lib/server/auth';

const defaultMetadata = {
  type: 'artist' as const,
  object: {
    uuid: '',
    slug: '',
    name: 'Artist Name',
    appUrl: '',
    imageUrl: '',
    countryCode: '',
    genres: [
      {
        root: '',
        sub: [],
      },
    ],
    biography: '',
    isni: '',
    ipi: '',
    gender: 'other' as const,
    type: 'person' as const,
    birthDate: '',
  },
  errors: [],
};

const defaultStreaming = {
  type: 'streaming' as const,
  object: {
    spotify: {
      monthlyListeners: 0,
      followers: 0,
      popularity: 0,
      playlists: 0,
    },
    appleMusic: {
      playlists: 0,
    },
    deezer: {
      fans: 0,
      playlists: 0,
    },
  },
  errors: [],
};

const defaultFollowers = {
  type: 'followers' as const,
  object: {
    total: 0,
    platforms: {
      spotify: 0,
      instagram: 0,
      youtube: 0,
      tiktok: 0,
      facebook: 0,
      twitter: 0,
    },
    history: [] as { date: string; count: number }[],
  },
  errors: [],
};

export const load = (async ({ locals }) => {
  const auth = requireAuth(locals);

  const artistData = await db
    .select()
    .from(artists)
    .where(eq(artists.orgId, locals.auth.orgId))
    .limit(1);

  if (!artistData.length) {
    return {
      auth,
      metadata: defaultMetadata,
      streaming: defaultStreaming,
      followers: defaultFollowers,
    };
  }

  try {
    const artist = artistData[0];
    const spotifyId = artist.spotify ? artist.spotify.split('/').pop() : null;

    if (!spotifyId) {
      return {
        auth,
        metadata: defaultMetadata,
        streaming: defaultStreaming,
        followers: defaultFollowers,
      };
    }

    const { metadata, streaming, followers } = await soundcharts.getArtistStats(spotifyId);

    return {
      auth,
      metadata: metadata,
      streaming: streaming,
      followers: followers,
    };
  } catch (err) {
    return {
      auth,
      metadata: defaultMetadata,
      streaming: defaultStreaming,
      followers: defaultFollowers,
    };
  }
}) satisfies PageServerLoad;
