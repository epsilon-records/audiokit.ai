/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { artistSchema } from '$lib/schemas/artist';
import { getOrg, requireAuth, requireOrg } from '$lib/server/auth';
import { syncToHubspot } from '$lib/server/integrations/hubspot';
import logger from '$lib/utils/logger';
import { sanitizeUrl } from '$lib/utils/sanitize';
import { error, fail } from '@sveltejs/kit';
import { sql } from 'drizzle-orm';
import { zod } from 'sveltekit-superforms/adapters';
import { message, superValidate } from 'sveltekit-superforms/server';
import type { PageServerLoad } from './$types';

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
      logger.warning(crypto.randomUUID(), 'Profile form validation failed', {
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

    // Sync the updated artist data to HubSpot
    if (updatedArtist.email) {
      const hubspotData = {
        email: updatedArtist.email,
        phone: updatedArtist.phone || null,
        city: updatedArtist.city || null,
        country: updatedArtist.country || null,
        biography: updatedArtist.biography || null,
        website: updatedArtist.website || null,
        spotify: updatedArtist.spotify || null,
        instagram: updatedArtist.instagram || null,
        twitterhandle: updatedArtist.x || null,
        soundcloud: updatedArtist.soundcloud || null,
      };
      await syncToHubspot(updatedArtist.email, hubspotData);
    } else {
      logger.warning(crypto.randomUUID(), 'Unable to sync to HubSpot due to missing email', {
        orgId: locals.auth.orgId,
      });
    }

    return message(form, 'Profile updated successfully!');
  },
};
