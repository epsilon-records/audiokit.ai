import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';
import { stripe } from '$lib/server/stripe';
import { db } from '$lib/db';
import { eq } from 'drizzle-orm';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/services/soundcharts';

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

  if (!artistData.length) {
    return {
      stats: null,
      hasActiveSubscription,
    };
  }

  try {
    const artist = artistData[0];
    const spotifyId = artist.spotify ? artist.spotify.split('/').pop() : null;

    if (!spotifyId) {
      return {
        stats: null,
        hasActiveSubscription,
      };
    }

    const stats = await soundcharts.getArtistStats(spotifyId);
    console.error('Successfully fetched stats:', stats);
    return {
      stats: {
        metadata: stats.metadata,
      },
      hasActiveSubscription,
    };
  } catch (err) {
    console.error('Error fetching stats:', err);
    return {
      stats: null,
      hasActiveSubscription,
    };
  }
};
