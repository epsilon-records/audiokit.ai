import { redirect } from '@sveltejs/kit';
import { invalidateAll } from '$app/navigation';

export const load = async () => {
  await invalidateAll();
  throw redirect(307, '/dashboard');
};
