import { stripe } from './stripe';
import { redirect } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function getStripeCustomerId(user: { id: string; emailAddresses: any[] }) {
  if (!user) return null;

  const email = user.emailAddresses[0]?.emailAddress;
  if (!email) return null;

  const [customer] = (await stripe.customers.list({ email, limit: 1 })).data;
  return customer?.id || null;
}

export function requireUser(locals: App.Locals) {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }
}

export function requireOrg(locals: App.Locals) {
  requireUser(locals);

  if (!locals.auth.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }
}

export function requireAuth(locals: App.Locals) {
  requireUser(locals);
  requireOrg(locals);
}
