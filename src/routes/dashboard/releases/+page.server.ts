import { requireAuth } from '$lib/server/auth';

export function load({ locals }) {
  const { auth } = requireAuth(locals);
  return { auth, releases: null };
}
