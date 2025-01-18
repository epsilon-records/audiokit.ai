import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';
import { clerkClient } from 'svelte-clerk/server';
import { soundcharts } from '$lib/services/soundcharts';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';

const stripe = new Stripe(STRIPE_SECRET_KEY);

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }

  const user = await clerkClient.users.getUser(locals.auth.userId);
  const email = user.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw redirect(307, '/sign-in');
  }

  // Check subscription status
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

  // Get artist data
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

  // Fetch stats from Soundcharts if we have an artist
  try {
    const artist = artistData[0];
    console.log(artist);

    // Extract Spotify ID from URL
    const spotifyId = artist.spotify ? artist.spotify.split('/').pop() : null;
    console.log(spotifyId);
    if (!spotifyId) {
      console.error('Spotify ID not found for artist');
      return {
        stats: null,
        hasActiveSubscription,
      };
    }

    const stats = await soundcharts.getArtistStats(spotifyId);

    return {
      stats: stats,
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
