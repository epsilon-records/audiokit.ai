import { error, json } from '@sveltejs/kit';
import { STRIPE_SECRET_KEY } from '$env/static/private';
import Stripe from 'stripe';

const stripe = new Stripe(STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
});

const PRICE_IDS = {
  'Basic Label': {
    monthly: 'price_1QhoEfGR0puR9CIOe4wDgU3r', // Replace with your Stripe price IDs
    annual: 'price_1Qhnp5GR0puR9CIOXUUBY41J',
  },
  'Pro Label': {
    monthly: 'price_1QiGyWGR0puR9CIOGQ8pos1G',
    annual: 'price_1QiGzbGR0puR9CIORzolPAvm',
  },
} as const;

export async function POST({ request, url }) {
  try {
    const { tier, isAnnual } = await request.json();

    // Validate tier exists
    if (!PRICE_IDS[tier as keyof typeof PRICE_IDS]) {
      throw error(400, 'Invalid pricing tier');
    }

    const priceId = PRICE_IDS[tier as keyof typeof PRICE_IDS][isAnnual ? 'annual' : 'monthly'];

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${url.origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${url.origin}/pricing`,
      automatic_tax: { enabled: false },
    });

    return json({ url: session.url });
  } catch (err) {
    console.error('Stripe session creation failed:', err);
    throw error(500, 'Could not create checkout session');
  }
}
