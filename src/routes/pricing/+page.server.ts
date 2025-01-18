import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.auth?.userId) {
    const user = await clerkClient.users.getUser(locals.auth.userId);
      return {
        meta: {
          title: 'Pricing - AudioKit',
          description: 'Simple, transparent pricing for all your music distribution needs',
        },
        email: user.primaryEmailAddress?.emailAddress ?? null,
      };
  }
  return {
    meta: {
      title: 'Pricing - AudioKit',
      description: 'Simple, transparent pricing for all your music distribution needs',
    },
    email: null,
  };
};
