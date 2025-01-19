import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';
import { clerkClient } from 'svelte-clerk/server';
import { page } from '$app/state';

const stripe = new Stripe(STRIPE_SECRET_KEY);

export const load: LayoutServerLoad = async ({ locals, depends }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }

  const user = await clerkClient.users.getUser(locals.auth.userId);
  let email = user.primaryEmailAddress?.emailAddress ?? null;

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
