import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(303, '/pricing');
  }

  const user = await clerkClient.users.getUser(locals.auth.userId);
  return {
    email: user.primaryEmailAddress?.emailAddress,
  };
};
