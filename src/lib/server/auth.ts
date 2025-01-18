import { stripe } from './stripe';

export async function getStripeCustomerId(user: { id: string; emailAddresses: any[] }) {
  if (!user) return null;

  const email = user.emailAddresses[0]?.emailAddress;
  if (!email) return null;

  const [customer] = (await stripe.customers.list({ email, limit: 1 })).data;
  return customer?.id || null;
}
