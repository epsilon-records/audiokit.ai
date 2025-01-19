import { error, json, type RequestHandler } from '@sveltejs/kit';
import { stripe } from '$lib/server/stripe';
import { getStripeCustomerId } from '$lib/server/auth';

export const POST: RequestHandler = async ({ locals }) => {
  try {
    // Get the current user's Stripe customer ID
    const customerId = await getStripeCustomerId(locals.user);

    if (!customerId) {
      throw error(400, 'No Stripe customer ID found');
    }

    // Create the portal session
    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${locals.origin}/dashboard`,
    });

    return json({ url: session.url });
  } catch (err) {
    throw error(500, 'Could not create portal session');
  }
};
