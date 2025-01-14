<script lang="ts">
  import SignIn from 'clerk-sveltekit/client/SignIn.svelte';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<div class="container relative z-10 px-4 flex flex-col items-center text-center">
  <SignIn
    appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
    redirectUrl="/my/settings/profile"
  />
</div>
