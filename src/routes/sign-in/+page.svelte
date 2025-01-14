<script lang="ts">
  import SignIn from 'clerk-sveltekit/client/SignIn.svelte';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="m-4">
    <SignIn
      appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
      redirectUrl="/my/settings/profile"
    />
  </div>
</div>
