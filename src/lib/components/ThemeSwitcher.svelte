<script lang="ts">
  import { mode, toggleMode } from 'mode-watcher';
  import { Sun, Moon, Icon } from 'svelte-hero-icons';
  import { Button } from '$lib/components/ui/button';
</script>

<Button
  variant="ghost"
  size="icon"
  onclick={toggleMode}
  class="hover:bg-accent hover:text-accent-foreground -mt-2"
  aria-label="Toggle theme"
>
  {#if $mode === 'dark'}
    <Icon src={Sun} class="h-5 w-5" />
  {:else}
    <Icon src={Moon} class="h-5 w-5" />
  {/if}
</Button>
