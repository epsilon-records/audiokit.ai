import { error, json } from '@sveltejs/kit';
import { STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET } from '$env/static/private';
import Stripe from 'stripe';

const stripe = new Stripe(STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
});

export async function POST({ request }) {
  const signature = request.headers.get('stripe-signature');

  if (!signature) {
    throw error(400, 'Missing stripe-signature header');
  }

  try {
    const body = await request.text();
    const event = stripe.webhooks.constructEvent(body, signature, STRIPE_WEBHOOK_SECRET);

    switch (event.type) {
      case 'checkout.session.completed':
        // Handle successful checkout
        break;
      case 'customer.subscription.updated':
        // Handle subscription updates
        break;
      case 'customer.subscription.deleted':
        // Handle subscription cancellations
        break;
    }

    return json({ received: true });
  } catch (err) {
    console.error('Webhook Error:', err);
    throw error(400, 'Webhook Error');
  }
}
