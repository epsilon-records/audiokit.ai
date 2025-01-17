<script lang="ts">
  import { SignUp } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
</script>

<svelte:head>
  <title>Sign Up | AudioKit</title>
  <meta name="description" content="Create your AudioKit account" />
</svelte:head>

<AuthContainer title="Create Account">
  <SignUp
    appearance={{
      baseTheme: $mode === 'dark' ? dark : neobrutalism,
      variables: {
        spacingUnit: '16px',
        borderRadius: '8px',
      },
    }}
    redirectUrl="/dashboard"
  />
</AuthContainer>
