import { redirect } from '@sveltejs/kit';
import { invalidateAll } from '$app/navigation';
import { browser } from '$app/environment';

export const load = async () => {
  if (browser) {
    invalidateAll();
    throw redirect(307, '/dashboard');
  }
  throw redirect(307, '/sign-in');
};
