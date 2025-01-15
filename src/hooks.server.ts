import { withClerkHandler } from 'svelte-clerk/server';
import { pb } from '$lib/pocketbase';
import { PB_SECRET_KEY } from '$env/static/private';
import { sequence } from '@sveltejs/kit/hooks';

export async function pocketbaseHandler({ event, resolve }: { event: any; resolve: any }) {
    await pb.collection("users").authWithPassword('pb@epsilonrecords.com', PB_SECRET_KEY);
    return resolve(event);
}

export const handle = sequence(withClerkHandler(), pocketbaseHandler);