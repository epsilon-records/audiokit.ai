<script lang="ts">
  import { UserProfile } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<div class="flex justify-center bg-background">
  <div class="bg-card rounded-lg p-2 mt-4 mb-8">
    <UserProfile
      appearance={{
        baseTheme: $mode === 'dark' ? dark : neobrutalism,
        variables: {
          spacingUnit: '16px',
          borderRadius: '8px',
        },
      }}
    />
  </div>
</div>
