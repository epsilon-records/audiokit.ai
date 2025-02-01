import { redirect } from '@sveltejs/kit';
import { invalidateAll } from '$app/navigation';
import logger from '$lib/utils/logger';

export const load = async () => {
  logger.debug({
    msg: 'Reloading dashboard',
  });
  await invalidateAll();
  throw redirect(307, '/dashboard');
};
