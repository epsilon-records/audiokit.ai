import { stripe } from './stripe';
import { redirect, error } from '@sveltejs/kit';
import { clerkClient } from 'svelte-clerk/server';
import Stripe from 'stripe';
import { STRIPE_SECRET_KEY } from '$env/static/private';

/**
 * Common error messages as constants to maintain consistency
 */
const AUTH_ERRORS = {
  NO_EMAIL: 'No email address found',
  INVALID_AUTH: 'Invalid authentication state',
  STRIPE_CUSTOMER_ERROR: 'Unable to create Stripe customer',
  SUBSCRIPTION_ERROR: 'Unable to verify subscription status',
} as const;

/**
 * Interface defining authentication state
 */
interface Auth {
  userId: string;
  orgId?: string;
  email?: string;
  customerId?: string;
  hasActiveSubscription?: boolean;
}

/**
 * Retrieves the primary email address for a given user
 * @param userId - The Clerk user ID
 * @returns The user's primary email address
 * @throws {error} 400 if no email address is found
 */
async function getUserEmail(userId: string) {
  const user = await clerkClient.users.getUser(userId);
  const email = user.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw error(400, AUTH_ERRORS.NO_EMAIL);
  }

  return email;
}

/**
 * Gets or creates a Stripe customer ID for a user
 * @param userId - The Clerk user ID
 * @returns The Stripe customer ID
 * @throws {error} 401 if no email found or invalid auth state
 */
async function getStripeCustomerId(userId: string) {
  const email = await getUserEmail(userId);

  const [existingCustomer] = (await stripe.customers.list({ email, limit: 1 })).data;

  if (existingCustomer) {
    return existingCustomer.id;
  }

  const newCustomer = await stripe.customers.create({
    email,
    metadata: {
      userId, // Link Stripe customer to Clerk user ID
    },
  });

  if (!newCustomer.id) {
    throw error(400, AUTH_ERRORS.STRIPE_CUSTOMER_ERROR);
  }

  return newCustomer.id;
}

/**
 * Ensures user is authenticated, redirects to sign-in if not
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing userId
 * @throws {redirect} to /sign-in if user is not authenticated
 */
function requireUser(locals: App.Locals): Auth {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }
  return { userId: locals.auth.userId };
}

/**
 * Ensures user has selected an organization/artist profile
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing userId and orgId
 * @throws {redirect} to /dashboard/create-artist if no org selected
 */
function requireOrg(locals: App.Locals): Auth {
  const auth = requireUser(locals);

  if (!locals.auth?.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }

  return { ...auth, orgId: locals.auth.orgId };
}

/**
 * Main authentication guard that ensures both user and org are valid
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing authenticated userId and orgId
 * @throws {error} 401 if authentication state is invalid
 */
export async function requireAuth(locals: App.Locals): Promise<Auth> {
  const auth = requireOrg(locals);
  const email = await getUserEmail(auth.userId);

  if (!auth.userId || !auth.orgId || !email) {
    throw error(401, AUTH_ERRORS.INVALID_AUTH);
  }

  return { ...auth, email };
}

/**
 * Ensures user has a valid Stripe customer ID
 * @param locals - SvelteKit app locals containing auth state
 * @returns Stripe customer ID
 * @throws {error} 401 if user is not authenticated
 * @throws {error} 400 if unable to get/create Stripe customer
 */
export async function requireCustomer(locals: App.Locals): Promise<Auth> {
  const auth = requireUser(locals);
  const email = await getUserEmail(auth.userId);
  const customerId = await getStripeCustomerId(auth.userId);

  return { ...auth, email, customerId };
}

/**
 * Subscription check
 */
export async function requireSubscription(locals: App.Locals): Promise<Auth> {
  const auth = await requireCustomer(locals);

  const [subscription] = (
    await stripe.subscriptions.list({
      customer: auth.customerId!,
      limit: 1,
      status: 'active',
    })
  ).data;

  return { ...auth, hasActiveSubscription: !!subscription };
}
