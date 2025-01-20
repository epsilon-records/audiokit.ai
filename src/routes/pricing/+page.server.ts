import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(303, '/subscription');
  }

  const user = await clerkClient.users.getUser(locals.auth.userId);
  return {
    meta: {
      title: 'Pricing - AudioKit',
      description: 'Simple, transparent pricing for all your music distribution needs',
    },
    email: user.primaryEmailAddress?.emailAddress ?? null,
  };
};
