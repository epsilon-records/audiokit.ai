import { withClerkHandler } from 'svelte-clerk/server';
import { initPocketBase } from '$lib/pocketbase';
import { sequence } from '@sveltejs/kit/hooks';
import type { Handle } from '@sveltejs/kit';

const pocketbaseHandle: Handle = async ({ event, resolve }) => {
    await initPocketBase();
    return await resolve(event);
};

export const handle = sequence(withClerkHandler(), pocketbaseHandle);