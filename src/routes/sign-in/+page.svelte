<script lang="ts">
  import { SignIn } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
</script>

<svelte:head>
  <title>Sign In | AudioKit</title>
  <meta name="description" content="Sign in to your AudioKit account" />
</svelte:head>

<AuthContainer title="Welcome Back">
  <SignIn
    appearance={{
      baseTheme: $mode === 'dark' ? dark : neobrutalism,
      variables: {
        spacingUnit: '16px',
        borderRadius: '8px',
      },
    }}
    fallbackRedirectUrl="/dashboard"
  />
</AuthContainer>
