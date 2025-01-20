<script lang="ts">
  import { SignUp } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
  import { createClerkAppearance } from '$lib/config/clerk';

  let appearance = $state(createClerkAppearance($mode === 'dark' ? 'dark' : 'light'));

  $effect(() => {
    appearance = createClerkAppearance($mode === 'dark' ? 'dark' : 'light');
  });
</script>

<svelte:head>
  <title>Sign Up | AudioKit</title>
  <meta name="description" content="Create your AudioKit account" />
</svelte:head>

<AuthContainer title="Create Account">
  <SignUp {appearance} fallbackRedirectUrl="/dashboard/redirect" />
</AuthContainer>
