import { db } from '$lib/db';
import { streamingAnalytics, socialAnalytics, revenueAnalytics } from '$lib/db/schema';
import type { PageServerLoad } from './$types';
import { desc, eq } from 'drizzle-orm';

export const load: PageServerLoad = async ({ locals }) => {
  try {
    const streamingData = await db
      .select()
      .from(streamingAnalytics)
      .where(eq(streamingAnalytics.orgId, locals.auth.orgId))
      .orderBy(desc(streamingAnalytics.timestamp))
      .limit(50);

    const socialData = await db
      .select()
      .from(socialAnalytics)
      .where(eq(socialAnalytics.orgId, locals.auth.orgId))
      .orderBy(desc(socialAnalytics.timestamp))
      .limit(50);

    const revenueData = await db
      .select()
      .from(revenueAnalytics)
      .where(eq(revenueAnalytics.orgId, locals.auth.orgId))
      .orderBy(desc(revenueAnalytics.timestamp))
      .limit(50);

    return {
      streaming: streamingData,
      social: socialData,
      revenue: revenueData,
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
      },
    };
  } catch (err) {
    console.error('Error loading analytics:', err);
    return {
      streaming: [],
      social: [],
      revenue: [],
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
      },
    };
  }
};
