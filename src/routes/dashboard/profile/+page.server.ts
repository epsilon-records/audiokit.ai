import { requireAuth } from '$lib/server/auth';
import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { artistSchema } from '$lib/schemas/artist';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);

  // Get artist data using Drizzle
  const artistData = await db
    .select()
    .from(artists)
    .where(eq(artists.orgId, locals.auth.orgId))
    .limit(1);

  let artist = {};
  if (artistData.length === 0) {
    // Create new artist if none exists
    const [newArtist] = await db
      .insert(artists)
      .values({
        orgId: locals.auth.orgId,
        created: new Date().toISOString(),
        updated: new Date().toISOString(),
      })
      .returning();
    artist = newArtist;
  } else {
    artist = artistData[0];
  }

  const form = await superValidate(artist, zod(artistSchema));

  return { auth, form };
}) satisfies PageServerLoad;

export const actions = {
  default: async ({ request, locals }) => {
    const form = await superValidate(request, zod(artistSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      // Get existing artist
      const existingArtist = await db
        .select()
        .from(artists)
        .where(eq(artists.orgId, locals.auth?.orgId))
        .limit(1);

      if (existingArtist.length === 0) {
        // Create new artist
        await db.insert(artists).values({
          ...form.data,
          orgId: locals.auth?.orgId,
          created: new Date().toISOString(),
          updated: new Date().toISOString(),
        });
      } else {
        // Update existing artist
        await db
          .update(artists)
          .set({
            ...form.data,
            updated: new Date().toISOString(),
          })
          .where(eq(artists.orgId, locals.auth?.orgId));
      }

      return message(form, 'Profile updated successfully!');
    } catch (err) {
      console.error('Error updating profile:', err);
      return message(form, 'Failed to update profile. Please try again.', {
        status: 500,
      });
    }
  },
};
