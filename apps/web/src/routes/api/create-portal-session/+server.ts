/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { stripe } from '$lib/server/stripe';
import { error, json } from '@sveltejs/kit';
import { clerkClient } from 'svelte-clerk/server';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ locals, url }) => {
  try {
    const user = await clerkClient.users.getUser(locals.auth.userId);
    const primaryEmail = user.emailAddresses.find(
      (email) => email.id === user.primaryEmailAddressId
    )?.emailAddress;
    if (!primaryEmail) {
      throw error(400, 'No email address found');
    }
    const customers = await stripe.customers.list({
      email: primaryEmail,
      limit: 1,
    });
    let customerId = customers.data[0]?.id;
    if (!customerId) {
      const newCustomer = await stripe.customers.create({
        email: primaryEmail,
        name: user.firstName ? `${user.firstName} ${user.lastName || ''}`.trim() : undefined,
      });
      customerId = newCustomer.id;
    }

    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${url.origin}/dashboard`,
    });
    return json({ url: session.url });
  } catch (err) {
    throw error(500, 'Could not create portal session');
  }
};
