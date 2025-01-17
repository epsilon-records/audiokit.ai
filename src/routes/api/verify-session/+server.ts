import { error, json } from '@sveltejs/kit';
import { STRIPE_SECRET_KEY } from '$env/static/private';
import Stripe from 'stripe';

const stripe = new Stripe(STRIPE_SECRET_KEY);

export async function POST({ request }) {
  try {
    const { sessionId } = await request.json();

    // Retrieve the session from Stripe
    const session = await stripe.checkout.sessions.retrieve(sessionId);

    // Verify the payment status
    if (session.payment_status !== 'paid') {
      throw error(400, 'Payment not completed');
    }

    // Here you would typically:
    // 1. Update your database with the user's subscription status
    // 2. Create or update the customer record
    // 3. Set up any necessary session data

    return json({ success: true });
  } catch (err) {
    console.error('Session verification error:', err);
    throw error(500, 'Could not verify checkout session');
  }
}
