import { error, json } from '@sveltejs/kit';
import {
  STRIPE_SECRET_KEY,
  STRIPE_LIVE_ARTIST_MONTHLY,
  STRIPE_LIVE_ARTIST_ANNUAL,
  STRIPE_LIVE_LABEL_MONTHLY,
  STRIPE_LIVE_LABEL_ANNUAL,
  STRIPE_TEST_ARTIST_MONTHLY,
  STRIPE_TEST_ARTIST_ANNUAL,
  STRIPE_TEST_LABEL_MONTHLY,
  STRIPE_TEST_LABEL_ANNUAL,
} from '$env/static/private';
import Stripe from 'stripe';

const stripe = new Stripe(STRIPE_SECRET_KEY);

const LIVE_PRICE_IDS = {
  '🎵 Individual Artist': {
    monthly: STRIPE_LIVE_ARTIST_MONTHLY,
    annual: STRIPE_LIVE_ARTIST_ANNUAL,
  },
  '⭐ Record Label': {
    monthly: STRIPE_LIVE_LABEL_MONTHLY,
    annual: STRIPE_LIVE_LABEL_ANNUAL,
  },
} as const;

const TEST_PRICE_IDS = {
  '🎵 Individual Artist': {
    monthly: STRIPE_TEST_ARTIST_MONTHLY,
    annual: STRIPE_TEST_ARTIST_ANNUAL,
  },
  '⭐ Record Label': {
    monthly: STRIPE_TEST_LABEL_MONTHLY,
    annual: STRIPE_TEST_LABEL_ANNUAL,
  },
} as const;

export async function POST({ request, url }) {
  try {
    const { tier, isAnnual, email } = await request.json();

    // Select price IDs based on environment
    const PRICE_IDS = import.meta.env.PROD ? LIVE_PRICE_IDS : TEST_PRICE_IDS;

    if (!PRICE_IDS[tier as keyof typeof PRICE_IDS]) {
      throw error(400, 'Invalid pricing tier');
    }

    const priceId = PRICE_IDS[tier as keyof typeof PRICE_IDS][isAnnual ? 'annual' : 'monthly'];
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      customer_email: email,
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${url.origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${url.origin}/dashboard`,
      automatic_tax: { enabled: false },
    });
    return json({ url: session.url });
  } catch (err) {
    throw error(500, 'Could not create checkout session');
  }
}
