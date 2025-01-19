import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';
import { stripe } from '$lib/server/stripe';
import { db } from '$lib/db';
import { eq } from 'drizzle-orm';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/services/soundcharts';

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

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }

  const user = await clerkClient.users.getUser(locals.auth.userId);
  const email = user.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw redirect(307, '/sign-in');
  }

  const [customer] = (await stripe.customers.list({ email, limit: 1 })).data;
  let hasActiveSubscription = false;

  if (customer) {
    const [subscription] = (
      await stripe.subscriptions.list({
        customer: customer.id,
        limit: 1,
        status: 'active',
      })
    ).data;
    hasActiveSubscription = !!subscription;
  }

  const artistData = await db
    .select()
    .from(artists)
    .where(eq(artists.orgId, locals.auth.orgId))
    .limit(1);

  // Fetch organization details
  const org = await clerkClient.organizations.getOrganization({
    organizationId: locals.auth.orgId,
  });

  if (!artistData.length) {
    return {
      stats: {
        metadata: defaultMetadata,
        streaming: defaultStreaming,
        followers: defaultFollowers,
      },
      hasActiveSubscription,
      user: {
        id: user.id,
        imageUrl: user.imageUrl,
      },
      org: {
        id: org.id,
        name: org.name,
        imageUrl: org.imageUrl,
      },
    };
  }

  try {
    const artist = artistData[0];
    const spotifyId = artist.spotify ? artist.spotify.split('/').pop() : null;

    if (!spotifyId) {
      return {
        stats: {
          metadata: defaultMetadata,
          streaming: defaultStreaming,
          followers: defaultFollowers,
        },
        hasActiveSubscription,
        user: {
          id: user.id,
          imageUrl: user.imageUrl,
        },
        org: {
          id: org.id,
          name: org.name,
          imageUrl: org.imageUrl,
        },
      };
    }

    const stats = await soundcharts.getArtistStats(spotifyId);
    console.error('Successfully fetched stats:', stats);
    return {
      stats: {
        metadata: stats.metadata,
        streaming: defaultStreaming,
        followers: defaultFollowers,
      },
      hasActiveSubscription,
      user: {
        id: user.id,
        imageUrl: user.imageUrl,
      },
      org: {
        id: org.id,
        name: org.name,
        imageUrl: org.imageUrl,
      },
    };
  } catch (err) {
    console.error('Error fetching stats:', err);
    return {
      stats: {
        metadata: defaultMetadata,
        streaming: defaultStreaming,
        followers: defaultFollowers,
      },
      hasActiveSubscription,
      user: {
        id: user.id,
        imageUrl: user.imageUrl,
      },
      org: {
        id: org.id,
        name: org.name,
        imageUrl: org.imageUrl,
      },
    };
  }
};
