import type { PageServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth';
import { clerkClient } from 'svelte-clerk/server';

export const load: PageServerLoad = async ({ locals }) => {
  const { auth } = requireAuth(locals);
  const user = await clerkClient.users.getUser(auth.userId);

  return {
    title: 'Get Started with AudioKit',
    description:
      'Choose the perfect plan for your music distribution needs with our straightforward pricing options.',
    email: user.primaryEmailAddress?.emailAddress,
  };
};
