import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {loadStripe} from '@stripe/stripe-js';
import { STRIPE_PUBLIC_KEY, STRIPE_PRICE_IDS } from '$env/static/private';

const stripe = await loadStripe(STRIPE_PUBLIC_KEY);
const PRICE_IDS = JSON.parse(STRIPE_PRICE_IDS);

export const load = (async ({ locals, url }) => {
  if (!locals.auth?.userId) {
    return redirect(307, '/sign-in');
  } else if (!locals.auth?.orgId) {
    return redirect(302, '/my/settings/create');
  }

  try {
    // Get current subscription if any
    const subscriptions = await stripe.subscriptions.list({
      customer: locals.auth.orgId,
      status: 'active',
      expand: ['data.plan.product']
    });

    // Get all products and prices
    const products = await stripe.products.list({
      active: true,
      expand: ['data.default_price']
    });

    const prices = await stripe.prices.list({
      active: true,
      type: 'recurring',
      expand: ['data.product']
    });

    // Format pricing data
    const plans = products.data.map(product => {
      const price = prices.data.find(p => p.product === product.id);
      return {
        id: price?.id || '',
        productId: product.id,
        name: product.name,
        description: product.description,
        price: price ? (price.unit_amount || 0) / 100 : 0,
        interval: price?.recurring?.interval || 'month',
        features: product.metadata.features ? JSON.parse(product.metadata.features) : [],
        isPopular: product.metadata.isPopular === 'true'
      };
    });

    return {
      currentPlan: subscriptions.data[0] || null,
      plans,
      customerId: locals.auth.orgId
    };
  } catch (err) {
    console.error('Error loading billing data:', err);
    throw error(500, 'Failed to load billing information');
  }
}) satisfies PageServerLoad;

export const actions = {
  subscribe: async ({ request, locals, url }) => {
    if (!locals.auth?.userId || !locals.auth?.orgId) {
      throw error(401, 'Unauthorized');
    }

    const data = await request.formData();
    const priceId = data.get('priceId')?.toString();

    if (!priceId || !PRICE_IDS.includes(priceId)) {
      throw error(400, 'Invalid price ID');
    }

    try {
      const session = await stripe.checkout.sessions.create({
        customer: locals.auth.orgId,
        line_items: [{ price: priceId, quantity: 1 }],
        mode: 'subscription',
        success_url: `${url.origin}/my/settings/billing?success=true`,
        cancel_url: `${url.origin}/my/settings/billing?canceled=true`,
        allow_promotion_codes: true,
        billing_address_collection: 'required',
        customer_update: {
          address: 'auto',
          name: 'auto'
        }
      });

      return { url: session.url };
    } catch (err) {
      console.error('Stripe session creation failed:', err);
      throw error(500, 'Failed to create checkout session');
    }
  },

  manageSubscription: async ({ locals, url }) => {
    if (!locals.auth?.orgId) {
      throw error(401, 'Unauthorized');
    }

    try {
      const session = await stripe.billingPortal.sessions.create({
        customer: locals.auth.orgId,
        return_url: `${url.origin}/my/settings/billing`
      });

      return { url: session.url };
    } catch (err) {
      console.error('Billing portal session creation failed:', err);
      throw error(500, 'Failed to create billing portal session');
    }
  }
}; 