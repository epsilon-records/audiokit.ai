import { stripe } from './stripe';
import { redirect, error } from '@sveltejs/kit';
import { clerkClient } from 'svelte-clerk/server';

/**
 * Common error messages as constants to maintain consistency
 */
export const AUTH_ERRORS = {
  NO_EMAIL: 'No email address found',
  INVALID_AUTH: 'Invalid authentication state',
  STRIPE_CUSTOMER_ERROR: 'Unable to create Stripe customer',
  SUBSCRIPTION_ERROR: 'Unable to verify subscription status',
} as const;

/**
 * Interface defining authentication state
 * @property userId - Unique identifier for the user from Clerk
 * @property orgId - Optional organization/artist profile identifier
 * @property email - User's primary email address
 * @property customerId - Stripe customer identifier
 * @property hasActiveSubscription - Indicates if user has an active Stripe subscription
 */
interface Auth {
  userId: string;
  orgId: string;
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
 * @throws {error} 400 if no email found
 * @throws {error} 400 if unable to create Stripe customer
 * @description
 * First attempts to find an existing Stripe customer by email.
 * If none exists, creates a new customer and links it to the Clerk user ID.
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
 * @throws {redirect} 307 to /sign-in if user is not authenticated
 * @description
 * Basic authentication check that ensures a user is logged in.
 * Used as a building block for more comprehensive auth checks.
 */
function requireUser(locals: App.Locals): Auth {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }
  return {
    userId: locals.auth.userId,
    orgId: locals.auth.orgId,
  };
}

/**
 * Ensures user has selected an organization/artist profile
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing userId and orgId
 * @throws {redirect} 307 to /dashboard/create-artist if no org selected
 * @throws {redirect} 307 to /sign-in if user is not authenticated
 * @description
 * Builds on requireUser to ensure the user has also selected an artist profile.
 * Essential for routes that require artist context.
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
 * Ensures user has a valid Stripe subscription
 * @param locals - SvelteKit app locals containing auth state
 * @returns Auth object with subscription status
 * @throws {error} Various errors from requireCustomer
 * @description
 * Comprehensive check that ensures:
 * 1. User is authenticated
 * 2. Has a valid Stripe customer ID
 * 3. Has an active subscription
 * Used to protect premium features and paid content.
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

export function redirectAuthenticated(
  locals: App.Locals,
  redirectCode: number,
  redirectUrl: string
) {
  if (locals.auth?.userId) {
    throw redirect(redirectCode, redirectUrl);
  }
}

export function redirectUnauthenticated(
  locals: App.Locals,
  redirectCode: number,
  redirectUrl: string
) {
  if (!locals.auth?.userId) {
    throw redirect(redirectCode, redirectUrl);
  }
}
