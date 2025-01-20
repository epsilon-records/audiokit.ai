import posthog from 'posthog-js';
import { browser } from '$app/environment';
import { onMount } from 'svelte';

onMount(() => {
  if (browser) {
    posthog.init('phc_j5S8Foca22TArMjuKIWR0DhyRt821XV9IqUY1mrOkQJ', {
      api_host: 'https://us.i.posthog.com',
      person_profiles: 'always',
    });
  }
});
