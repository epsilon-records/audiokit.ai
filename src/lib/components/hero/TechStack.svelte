<script lang="ts">
  import { fade } from 'svelte/transition';
  import { siOpenapiinitiative, siGraphql, siNpm } from 'simple-icons';

  let { ANIMATION_BASE_DELAY } = $props();
</script>

<div
  in:fade={{ duration: 1000, delay: ANIMATION_BASE_DELAY + 800 }}
  class="w-full max-w-lg space-y-6 pt-8 border-t border-border/40"
>
  <div class="inline-block">
    <p class="text-lg text-muted-foreground bg-white">Integrate With Your Stack</p>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
    <div
      class="flex flex-col items-center space-y-2 p-4 rounded-lg border-2 border-black bg-white transition-transform duration-300 hover:scale-[1.04]"
    >
      <svg class="w-6 h-6 text-primary" viewBox="0 0 24 24">
        <path fill="currentColor" d={siOpenapiinitiative.path} />
      </svg>
      <span class="text-sm font-medium">REST API</span>
    </div>
    <div
      class="flex flex-col items-center space-y-2 p-4 rounded-lg border-2 border-black bg-white transition-transform duration-300 hover:scale-[1.04]"
    >
      <svg class="w-6 h-6 text-primary" viewBox="0 0 24 24">
        <path fill="currentColor" d={siGraphql.path} />
      </svg>
      <span class="text-sm font-medium">GraphQL</span>
    </div>
    <div
      class="flex flex-col items-center space-y-2 p-4 rounded-lg border-2 border-black bg-white transition-transform duration-300 hover:scale-[1.04]"
    >
      <svg
        class="w-6 h-6 text-primary"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M18 16.98h-5.99c-1.1 0-1.95.94-2.48 1.9A4 4 0 0 1 2 17c.01-.7.2-1.4.57-2" />
        <path d="m6 17 3.13-5.78c.53-.97.1-2.18-.5-3.1a4 4 0 1 1 6.89-4.06" />
        <path d="m12 6 3.13 5.73C15.66 12.7 16.9 13 18 13a4 4 0 0 1 0 8" />
      </svg>
      <span class="text-sm font-medium">Webhooks</span>
    </div>
    <div
      class="flex flex-col items-center space-y-2 p-4 rounded-lg border-2 border-black bg-white transition-transform duration-300 hover:scale-[1.04]"
    >
      <svg class="w-6 h-6 text-primary" viewBox="0 0 24 24">
        <path fill="currentColor" d={siNpm.path} />
      </svg>
      <span class="text-sm font-medium">SDKs</span>
    </div>
  </div>
</div>
