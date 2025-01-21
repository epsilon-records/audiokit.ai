import { stripe } from './stripe';
import { redirect, error } from '@sveltejs/kit';
import { clerkClient } from 'svelte-clerk/server';

/**
 * Fetches user details from Clerk authentication service
 * @param userId - The Clerk user ID
 * @returns The Clerk user object
 * @throws {error} 401 if unable to fetch user details
 */
async function getClerkUser(userId: string) {
  try {
    const user = await clerkClient.users.getUser(userId);
    return user;
  } catch (err) {
    throw error(401, 'Unable to fetch user details');
  }
}

/**
 * Gets or creates a Stripe customer ID for a user
 * @param userId - The Clerk user ID
 * @returns The Stripe customer ID
 * @throws {error} 401 if no email found or invalid auth state
 */
async function getStripeCustomerId(userId: string) {
  const user = await getClerkUser(userId);

  // Get primary email address
  const email = user.emailAddresses[0]?.emailAddress;

  if (!email) {
    throw error(401, 'Invalid authentication state');
  }

  // Try to find existing customer
  const [existingCustomer] = (await stripe.customers.list({ email, limit: 1 })).data;

  if (existingCustomer) {
    return existingCustomer.id;
  }

  // Create new customer if none exists
  const newCustomer = await stripe.customers.create({
    email,
    metadata: {
      userId, // Link Stripe customer to Clerk user ID
    },
  });

  return newCustomer.id;
}

/**
 * Ensures user is authenticated, redirects to sign-in if not
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing userId
 * @throws {redirect} to /sign-in if user is not authenticated
 */
function requireUser(locals: App.Locals): { userId: string } {
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
function requireOrg(locals: App.Locals): { userId: string; orgId: string } {
  const { userId } = requireUser(locals);

  if (!locals.auth?.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }

  return { userId, orgId: locals.auth.orgId };
}

/**
 * Main authentication guard that ensures both user and org are valid
 * @param locals - SvelteKit app locals containing auth state
 * @returns Object containing authenticated userId and orgId
 * @throws {error} 401 if authentication state is invalid
 */
export function requireAuth(locals: App.Locals): { auth: { userId: string; orgId: string } } {
  const { userId, orgId } = requireOrg(locals);

  if (!userId || !orgId) {
    throw error(401, 'Invalid authentication state');
  }

  return {
    auth: { userId, orgId },
  };
}

/**
 * Ensures user has a valid Stripe customer ID
 * @param locals - SvelteKit app locals containing auth state
 * @returns Stripe customer ID
 * @throws {error} 401 if user is not authenticated
 * @throws {error} 400 if unable to get/create Stripe customer
 */
export async function requireCustomer(locals: App.Locals): Promise<string> {
  const { userId } = requireUser(locals);

  if (!userId) {
    throw error(401, 'Invalid authentication state');
  }

  const customerId = await getStripeCustomerId(userId);

  if (!customerId) {
    throw error(400, 'Unable to find or create Stripe customer.');
  }

  return customerId;
}
