import { requireAuth } from '$lib/server/auth';

export function load({ locals }) {
  const { auth } = requireAuth(locals);

  return {
    auth,
    streaming: null,
    social: null,
    revenue: null,
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      end: new Date(),
    },
  };
}
