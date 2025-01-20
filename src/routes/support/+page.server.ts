import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { clerkClient } from 'svelte-clerk/server';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';

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
