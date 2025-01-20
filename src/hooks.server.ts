import * as Sentry from '@sentry/sveltekit';
import { withClerkHandler } from 'svelte-clerk/server';
import { pb } from '$lib/pocketbase';
import { PB_SECRET_KEY } from '$env/static/private';
import { sequence } from '@sveltejs/kit/hooks';
import '@stripe/stripe-js';

Sentry.init({
    dsn: "https://b89f1762b68462bece4cd38d79eca72f@o337159.ingest.us.sentry.io/4508676068540416",
    tracesSampleRate: 1
})

const pocketbaseHandler = async ({ event, resolve }: { event: any; resolve: any }) => {
  await pb.collection('users').authWithPassword('pb@epsilonrecords.com', PB_SECRET_KEY);
  return resolve(event);
};

export const handle = sequence(Sentry.sentryHandle(), sequence(withClerkHandler(), pocketbaseHandler));
export const handleError = Sentry.handleErrorWithSentry();