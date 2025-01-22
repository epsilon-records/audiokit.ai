import { handleErrorWithSentry, replayIntegration } from '@sentry/sveltekit';
import * as Sentry from '@sentry/sveltekit';
import posthog from 'posthog-js';

Sentry.init({
  dsn: 'https://b89f1762b68462bece4cd38d79eca72f@o337159.ingest.us.sentry.io/4508676068540416',

  tracesSampleRate: 1.0,

  // This sets the sample rate to be 10%. You may want this to be 100% while
  // in development and sample at a lower rate in production
  replaysSessionSampleRate: 1.0,

  // If the entire session is not sampled, use the below sample rate to sample
  // sessions when an error occurs.
  replaysOnErrorSampleRate: 1.0,

  // If you don't want to use Session Replay, just remove the line below:
  integrations: [replayIntegration()],
});

posthog.init('phc_j5S8Foca22TArMjuKIWR0DhyRt821XV9IqUY1mrOkQJ', {
  api_host: 'https://us.i.posthog.com',
  person_profiles: 'always',
});

// If you have a custom error handler, pass it to `handleErrorWithSentry`
export const handleError = handleErrorWithSentry();
