import type { PageServerLoad } from './$types';
import { clerkClient } from 'svelte-clerk/server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.auth?.userId) {
    throw redirect(303, '/join');
  }

  return {
    title: 'Simple, Transparent Pricing',
    description:
      'Choose the perfect plan for your music distribution needs with our straightforward pricing options.',
    email: null,
  };
};
