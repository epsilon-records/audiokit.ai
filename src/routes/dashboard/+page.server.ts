import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { eq } from 'drizzle-orm';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/server/soundcharts';
import { getUser, getOrg, requireAuth } from '$lib/server/auth';

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
    location: '',
    websiteUrl: '',
    labels: [],
    status: 'active' as const,
    createdAt: '',
    updatedAt: '',
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
      topCities: [],
      topTracks: [],
    },
    appleMusic: {
      playlists: 0,
      rank: 0,
      listeners: 0,
    },
    deezer: {
      fans: 0,
      playlists: 0,
      rank: 0,
    },
    amazonMusic: {
      rank: 0,
      playlists: 0,
    },
    youtubeMusic: {
      subscribers: 0,
      views: 0,
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
      soundcloud: 0,
      bandcamp: 0,
    },
    history: [] as { date: string; count: number }[],
    engagement: {
      instagram: {
        avgLikes: 0,
        avgComments: 0,
        engagementRate: 0,
      },
      tiktok: {
        avgLikes: 0,
        avgComments: 0,
        avgShares: 0,
        engagementRate: 0,
      },
      youtube: {
        avgViews: 0,
        avgLikes: 0,
        avgComments: 0,
        engagementRate: 0,
      },
    },
  },
  errors: [],
};

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  const user = await getUser(auth.userId);
  const org = await getOrg(auth.orgId);

  const artistData = await db
    .select()
    .from(artists)
    .where(eq(artists.orgId, locals.auth.orgId))
    .limit(1);

  if (!artistData.length) {
    return {
      auth,
      user,
      org,
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
        user,
        org,
        metadata: defaultMetadata,
        streaming: defaultStreaming,
        followers: defaultFollowers,
      };
    }

    const { metadata, streaming, followers } = await soundcharts.getArtistStats(spotifyId);

    return {
      auth,
      user,
      org,
      metadata,
      streaming,
      followers,
    };
  } catch (err) {
    console.error('Error in dashboard load:', err);
    return {
      auth,
      user,
      org,
      metadata: defaultMetadata,
      streaming: defaultStreaming,
      followers: defaultFollowers,
    };
  }
}) satisfies PageServerLoad;
