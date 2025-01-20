import * as Sentry from '@sentry/sveltekit';
import { withClerkHandler } from 'svelte-clerk/server';
import { sequence } from '@sveltejs/kit/hooks';
import '@stripe/stripe-js';

Sentry.init({
  dsn: 'https://b89f1762b68462bece4cd38d79eca72f@o337159.ingest.us.sentry.io/4508676068540416',
  tracesSampleRate: 1,
});

export const handle = sequence(Sentry.sentryHandle(), sequence(withClerkHandler()));
export const handleError = Sentry.handleErrorWithSentry();
