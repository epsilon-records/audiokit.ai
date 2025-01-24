import { requireAuth, requireOrg, getOrg } from '$lib/server/auth';
import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { artistSchema } from '$lib/schemas/artist';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { sql } from 'drizzle-orm';
import { debug, warn } from '$lib/utils/logger';

// Add this helper function at the top of the file
function sanitizeUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  try {
    const urlObj = new URL(url);
    return urlObj.origin + urlObj.pathname;
  } catch {
    return url;
  }
}

export const load = (async ({ locals }) => {
  const auth = await requireOrg(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  // Get organization details
  const org = await getOrg(auth.orgId);
  if (!org) {
    throw error(404, 'Organization not found');
  }

  // Get or create artist data using Drizzle
  const [existingArtist] = await db
    .select()
    .from(artists)
    .where(sql`${artists.orgId} = ${auth.orgId}`);

  const artist =
    existingArtist ||
    (await db
      .insert(artists)
      .values({
        orgId: auth.orgId,
        created: new Date(),
        updated: new Date(),
      })
      .returning()
      .then((rows) => rows[0]));

  if (!artist) {
    throw error(500, 'Failed to create or retrieve artist record');
  }

  // Create mergedData with org.name as stageName
  const mergedData = {
    ...artist,
    stageName: org.name,
  };

  const formData = Object.fromEntries(
    Object.entries(mergedData).map(([key, value]) => [key, value === null ? undefined : value])
  );

  const form = await superValidate(formData, zod(artistSchema));

  return { auth, form };
}) satisfies PageServerLoad;

export const actions = {
  default: async ({ request, locals }) => {
    const auth = await requireAuth(locals);
    if (!auth) {
      throw error(401, 'Unauthorized');
    }

    const form = await superValidate(request, zod(artistSchema));
    if (!form.valid) {
      warn('Profile form validation failed', {
        errors: form.errors,
        orgId: auth.orgId,
      });
      return fail(400, { form });
    }

    // Sanitize all URL fields
    const sanitizedData = {
      ...form.data,
      website: sanitizeUrl(form.data.website),
      spotify: sanitizeUrl(form.data.spotify),
      instagram: sanitizeUrl(form.data.instagram),
      facebook: sanitizeUrl(form.data.facebook),
      x: sanitizeUrl(form.data.x),
      youtube: sanitizeUrl(form.data.youtube),
      tiktok: sanitizeUrl(form.data.tiktok),
    };

    const [updatedArtist] = await db
      .insert(artists)
      .values({
        ...sanitizedData,
        soundchartsId: form.data.soundchartsId,
        orgId: locals.auth.orgId,
        created: new Date(),
        updated: new Date(),
      })
      .onConflictDoUpdate({
        target: artists.orgId,
        set: {
          ...sanitizedData,
          soundchartsId: form.data.soundchartsId,
          updated: new Date(),
        },
      })
      .returning();

    if (!updatedArtist) {
      throw new Error('Failed to update artist record');
    }

    return message(form, 'Profile updated successfully!');
  },
};
