<script lang="ts">
  import { SignIn } from 'svelte-clerk';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
  import { createClerkAppearance } from '$lib/config/clerk';
</script>

<svelte:head>
  <title>Sign In | AudioKit</title>
  <meta name="description" content="Sign in to your AudioKit account" />
</svelte:head>

<AuthContainer title="Welcome Back">
  <SignIn appearance={createClerkAppearance()} fallbackRedirectUrl="/dashboard" />
</AuthContainer>
