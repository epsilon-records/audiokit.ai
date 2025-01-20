<script lang="ts">
  import { SignIn } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
  import { createClerkAppearance } from '$lib/config/clerk';

  let appearance = $state(createClerkAppearance($mode === 'dark' ? 'dark' : 'light'));

  $effect(() => {
    appearance = createClerkAppearance($mode === 'dark' ? 'dark' : 'light');
  });
</script>

<svelte:head>
  <title>Sign In | AudioKit</title>
  <meta name="description" content="Sign in to your AudioKit account" />
</svelte:head>

<AuthContainer title="Welcome Back">
  <SignIn {appearance} fallbackRedirectUrl="/" />
</AuthContainer>
