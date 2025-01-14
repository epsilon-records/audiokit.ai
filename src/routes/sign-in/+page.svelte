<script lang="ts">
  import SignIn from 'clerk-sveltekit/client/SignIn.svelte';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
</script>

<AuthContainer title="Sign In">
  <SignIn
    appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
    redirectUrl="/my/settings/profile"
  />
</AuthContainer>
