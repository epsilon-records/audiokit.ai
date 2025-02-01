import { PUBLIC_ORIGIN } from '$env/static/public';
import { requireCustomer } from '$lib/server/auth';
import { stripe } from '$lib/server/stripe';
import { error, json, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals }) => {
  const { customerId } = await requireCustomer(locals);

  try {
    if (!customerId) {
      throw error(400, 'No customer ID found');
    }
    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${PUBLIC_ORIGIN}/dashboard`,
    });
    return json({ url: session.url });
  } catch (err) {
    throw error(500, 'Could not create portal session');
  }
};
