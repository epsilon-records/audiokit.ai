import type { PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { releaseSchema } from '$lib/schemas/release';
import { requireAuth } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  const form = await superValidate(zod(releaseSchema));

  return {
    auth,
    form,
  };
}) satisfies PageServerLoad;
