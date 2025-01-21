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
 * Authentication state interface
 * @interface Auth
 * @property {string} userId - Clerk user identifier
 * @property {string} orgId - Organization/artist profile identifier
 * @property {string} [email] - User's primary email address
 * @property {string} [customerId] - Stripe customer identifier
 * @property {boolean} [hasActiveSubscription] - Whether user has active Stripe subscription
 */
interface Auth {
  userId: string;
  orgId: string;
  email?: string;
  customerId?: string;
  hasActiveSubscription?: boolean;
}

/**
 * Retrieves user's primary email address from Clerk
 * @async
 * @param {string} userId - The unique identifier of the Clerk user
 * @returns {Promise<string>} The user's primary email address
 * @throws {Error} 400 error if no primary email is associated with the account
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
 * Retrieves an existing Stripe customer or creates a new one for the user
 * @async
 * @param {string} userId - The unique identifier of the Clerk user
 * @returns {Promise<string>} The Stripe customer ID
 * @throws {Error} 400 error if email not found or Stripe customer creation fails
 */
async function getOrCreateStripeCustomer(userId: string) {
  const user = await clerkClient.users.getUser(userId);
  const email = user.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw error(400, AUTH_ERRORS.NO_EMAIL);
  }

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
 * Basic auth guard requiring user login
 * @param {App.Locals} locals - SvelteKit app locals
 * @returns {Auth} Authentication state with userId and orgId
 * @throws {redirect} 307 to /sign-in if authentication guard fails
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
 * Auth guard ensuring user has selected an organization
 * @param {App.Locals} locals - SvelteKit application locals containing auth state
 * @returns {Auth} Authentication state containing userId and orgId
 * @throws {Error} Redirects to /sign-in if auth guard fails or /dashboard/create-artist if org guard fails
 */
async function requireOrg(locals: App.Locals): Promise<Auth> {
  const auth = requireUser(locals);

  if (!locals.auth?.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }

  // Validate org exists
  await getOrg(locals.auth.orgId);

  return { ...auth, orgId: locals.auth.orgId };
}

/**
 * Auth guard ensuring user has Stripe customer account
 * @async
 * @param {App.Locals} locals - SvelteKit application locals containing auth state
 * @returns {Promise<Auth>} Authentication state with Stripe customer information
 * @throws {Error} 401 if auth guard fails, 400 if Stripe guard fails
 */
async function requireCustomer(locals: App.Locals): Promise<Auth> {
  const auth = requireUser(locals);
  const email = await getUserEmail(auth.userId);
  const customerId = await getOrCreateStripeCustomer(auth.userId);

  return { ...auth, email, customerId };
}

/**
 * Auth guard ensuring user has active subscription
 * @async
 * @param {App.Locals} locals - SvelteKit application locals containing auth state
 * @returns {Promise<Auth>} Authentication state including subscription status
 * @throws {Error} Various errors from customer verification and subscription guard
 * @throws {redirect} 307 to billing page if no active subscription
 */
async function requireSubscription(locals: App.Locals): Promise<Auth> {
  const auth = await requireCustomer(locals);

  const [subscription] = (
    await stripe.subscriptions.list({
      customer: auth.customerId!,
      limit: 1,
      status: 'active',
    })
  ).data;

  if (!subscription) {
    throw redirect(307, '/dashboard/billing');
  }

  return { ...auth, hasActiveSubscription: true };
}

/**
 * Redirects authenticated users
 * @param {App.Locals} locals - SvelteKit app locals
 * @param {number} redirectCode - HTTP redirect status code
 * @param {string} redirectUrl - Destination URL
 * @throws {redirect} If user is authenticated
 */
export function redirectAuthenticated(
  locals: App.Locals,
  redirectCode: number,
  redirectUrl: string
) {
  if (locals.auth?.userId) {
    throw redirect(redirectCode, redirectUrl);
  }
}

/**
 * Redirects unauthenticated users
 * @param {App.Locals} locals - SvelteKit app locals
 * @param {number} redirectCode - HTTP redirect status code
 * @param {string} redirectUrl - Destination URL
 * @throws {redirect} If user is not authenticated
 */
export function redirectUnauthenticated(
  locals: App.Locals,
  redirectCode: number,
  redirectUrl: string
) {
  if (!locals.auth?.userId) {
    throw redirect(redirectCode, redirectUrl);
  }
}

/**
 * Fetches detailed user information from Clerk
 * @async
 * @param {string} userId - The unique identifier of the Clerk user
 * @returns {Promise<Object>} Comprehensive user profile including personal and account details
 * @throws {Error} 400 error if user data cannot be retrieved
 */
async function getUser(userId: string) {
  try {
    const user = await clerkClient.users.getUser(userId);
    return {
      id: user.id,
      firstName: user.firstName,
      lastName: user.lastName,
      username: user.username,
      email: user.primaryEmailAddress?.emailAddress,
      phone: user.primaryPhoneNumber?.phoneNumber,
      imageUrl: user.imageUrl,
      lastSignedInAt: user.lastSignInAt,
      createdAt: user.createdAt,
    };
  } catch (err) {
    throw error(400, 'Unable to fetch user details');
  }
}

/**
 * Fetches detailed organization information from Clerk
 * @async
 * @param {string} orgId - The unique identifier of the Clerk organization
 * @returns {Promise<Object>} Comprehensive organization profile including membership details
 * @throws {Error} 400 error if organization data cannot be retrieved
 */
async function getOrg(orgId: string) {
  try {
    const org = await clerkClient.organizations.getOrganization({ organizationId: orgId });
    return {
      id: org.id,
      name: org.name,
      slug: org.slug,
      imageUrl: org.imageUrl,
      membersCount: org.membersCount,
      maxAllowedMemberships: org.maxAllowedMemberships,
      createdAt: org.createdAt,
      updatedAt: org.updatedAt,
    };
  } catch (err) {
    throw error(400, 'Unable to fetch organization details');
  }
}

export { requireCustomer, requireSubscription, getUser, getOrg };
