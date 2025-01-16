import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
  throw redirect(308, 'https://www.labelradar.com/labels/epsilonrecords/portal');
}; 