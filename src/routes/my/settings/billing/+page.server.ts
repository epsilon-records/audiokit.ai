// import { redirect } from '@sveltejs/kit';
// import type { PageServerLoad } from './$types';

// export const load: PageServerLoad = async () => {
//     throw redirect(302, 'https://buy.stripe.com/aEU9CLa1abUDcNy145');
// };

// import { error, fail, redirect } from '@sveltejs/kit';
// import type { PageServerLoad } from './$types';
// import Stripe from 'stripe';
// import { STRIPE_SECRET_KEY, STRIPE_PRICE_IDS } from '$env/static/private';

// const stripe = new Stripe(STRIPE_SECRET_KEY);

// export const load = (async ({ locals, url }) => {
//     const PRICE_IDS = JSON.parse(STRIPE_PRICE_IDS);
//     if (!locals.auth?.userId) {
//         throw redirect(307, '/sign-in');
//     } else if (!locals.auth?.orgId) {
//         throw redirect(302, '/my/settings/create');
//     } else if (!stripe) {
//         throw error(500, 'Internal server error');
//     }

//   try {
//     // Get current subscription if any
//     const subscriptions = await stripe.subscriptions.list({
//       customer: locals.auth.orgId,
//       status: 'active',
//       expand: ['data.plan.product']
//     });

//     // Get all products and prices
//     const products = await stripe.products.list({
//       active: true,
//       expand: ['data.default_price']
//     });

//     const prices = await stripe.prices.list({
//       active: true,
//       type: 'recurring',
//       expand: ['data.product']
//     });

//     // Format pricing data
//     const plans = products.data.map((product: any) => {
//       const price = prices.data.find((p: any) => p.product === product.id);
//       return {
//         id: price?.id || '',
//         productId: product.id,
//         name: product.name,
//         description: product.description,
//         price: price ? (price.unit_amount || 0) / 100 : 0,
//         interval: price?.recurring?.interval || 'month',
//         features: product.metadata.features ? JSON.parse(product.metadata.features) : [],
//         isPopular: product.metadata.isPopular === 'true'
//       };
//     });

//     return {
//       currentPlan: subscriptions.data[0] || null,
//       plans,
//       customerId: locals.auth.orgId
//     };
//   } catch (err) {
//     console.error('Error loading billing data:', err);
//     throw error(500, 'Internal server error');
//   }
// }) satisfies PageServerLoad;

// export const actions = {
//   subscribe: async ({ request, locals, url }) => {
//     const PRICE_IDS = JSON.parse(STRIPE_PRICE_IDS);
    
//     if (!locals.auth?.userId || !locals.auth?.orgId) {
//       throw error(401, 'Unauthorized');
//     }

//     const data = await request.formData();
//     const priceId = data.get('priceId')?.toString();

//     if (!priceId || !PRICE_IDS.includes(priceId)) {
//       throw error(400, 'Invalid price ID');
//     }

//     try {
//       const session = await stripe.checkout.sessions.create({
//         customer: locals.auth.orgId,
//         line_items: [{ price: priceId, quantity: 1 }],
//         mode: 'subscription',
//         success_url: `${url.origin}/my/settings/billing?success=true`,
//         cancel_url: `${url.origin}/my/settings/billing?canceled=true`,
//         allow_promotion_codes: true,
//         billing_address_collection: 'required',
//         customer_update: {
//           address: 'auto',
//           name: 'auto'
//         }
//       });

//       return { url: session.url };
//     } catch (err) {
//       console.error('Stripe session creation failed:', err);
//       throw error(500, 'Internal server error');
//     }
//   },

//   manageSubscription: async ({ locals, url }) => {
//     if (!locals.auth?.orgId) {
//       throw error(401, 'Unauthorized');
//     }

//     try {
//       const session = await stripe.billingPortal.sessions.create({
//         customer: locals.auth.orgId,
//         return_url: `${url.origin}/my/settings/billing`
//       });

//       return { url: session.url };
//     } catch (err) {
//       console.error('Billing portal session creation failed:', err);
//       throw error(500, 'Internal server error');
//     }
//   }
// }; 