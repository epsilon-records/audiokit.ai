import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.auth?.userId) {
    const user = await clerkClient.users.getUser(locals.auth.userId);
    return {
      email: user.primaryEmailAddress?.emailAddress ?? null,
    };
  }
  return {
    email: null,
  };
};
