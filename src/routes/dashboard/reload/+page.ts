import { redirect } from '@sveltejs/kit';
import { invalidateAll } from '$app/navigation';
import { debug } from '$lib/utils/logger';

export const load = async () => {
  debug({
    msg: 'Reloading dashboard',
  });
  await invalidateAll();
  throw redirect(307, '/dashboard');
};
