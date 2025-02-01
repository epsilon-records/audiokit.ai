import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { getOrg, getUser, requireAuth } from '$lib/server/auth';
import type { Artist } from '$lib/types';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const user = await getUser(auth.userId);
  if (!user) {
    throw error(404, 'User not found');
  }

  const org = await getOrg(auth.orgId);
  if (!org) {
    throw error(404, 'Organization not found');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  return {
    auth,
    user: {
      ...user,
      emailAddresses: (user.emailAddresses?.map((email) => email.emailAddress) ?? []) as string[],
      phoneNumbers: (user.phoneNumbers?.map((phone) => phone.phoneNumber) ?? []) as string[],
    },
    org,
    artist: artist as Artist,
  };
}) satisfies PageServerLoad;
