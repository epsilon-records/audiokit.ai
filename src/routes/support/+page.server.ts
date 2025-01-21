import type { PageServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth';
import { clerkClient } from 'svelte-clerk/server';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';
import { error } from '@sveltejs/kit';

const stripe = new Stripe(STRIPE_SECRET_KEY);

export const load: PageServerLoad = async ({ locals }) => {
  const { auth } = requireAuth(locals);
  const user = await clerkClient.users.getUser(auth.userId);
  const email = user.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw error(400, 'No email address found');
  }

  const [customer] = (
    await stripe.customers.list({
      email: email,
      limit: 1,
    })
  ).data;

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

  return {
    hasActiveSubscription,
  };
};
