import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';

const stripe = new Stripe(STRIPE_SECRET_KEY);

interface StripePlan {
    id: string;
    interval: 'month' | 'year';
    amount: number;
}

interface SubscriptionData {
    id: string;
    status: Stripe.Subscription.Status;
    current_period_end: number;
    cancel_at_period_end: boolean;
    plan: StripePlan;
}

export const load = (async ({ locals }) => {
    const { auth } = locals;
    
    if (!auth?.userId) {
        throw redirect(307, '/sign-in');
    }

    try {
        const [customer] = (await stripe.customers.list({
            email: auth.email,
            limit: 1
        })).data;

        if (!customer) {
            return { subscription: null };
        }

        const [subscription] = (await stripe.subscriptions.list({
            customer: customer.id,
            limit: 1,
            status: 'active',
            expand: ['data.plan']
        })).data;

        if (!subscription) {
            return { subscription: null };
        }

        const plan = subscription.items.data[0]?.plan;

        const subscriptionData: SubscriptionData = {
            id: subscription.id,
            status: subscription.status,
            current_period_end: subscription.current_period_end,
            cancel_at_period_end: subscription.cancel_at_period_end,
            plan: {
                id: plan?.id ?? '',
                interval: plan?.interval as 'month' | 'year',
                amount: (plan?.amount ?? 0) / 100
            }
        };

        return { subscription: subscriptionData };
    } catch (err) {
        console.error('Error fetching subscription:', err);
        throw error(500, 'Failed to fetch subscription details');
    }
}) satisfies PageServerLoad; 