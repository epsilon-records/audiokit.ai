<script lang="ts">
  import { SignUp } from 'svelte-clerk';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
  import { createClerkAppearance } from '$lib/config/clerk';
</script>

<svelte:head>
  <title>Sign Up | AudioKit</title>
  <meta name="description" content="Create your AudioKit account" />
</svelte:head>

<AuthContainer title="Create Account">
  <SignUp appearance={createClerkAppearance()} fallbackRedirectUrl="/dashboard" />
</AuthContainer>
