<script lang="ts">
  import SignUp from 'clerk-sveltekit/client/SignUp.svelte';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import AuthContainer from '$lib/components/AuthContainer.svelte';
</script>

<AuthContainer title="Sign Up">
  <SignUp
    appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
    redirectUrl="/my/settings/profile"
  />
</AuthContainer>
