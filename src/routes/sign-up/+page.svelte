<script lang="ts">
  import SignUp from 'clerk-sveltekit/client/SignUp.svelte';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="m-4">
    <SignUp
      appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
      redirectUrl="/my/settings/profile"
    />
  </div>
</div>
