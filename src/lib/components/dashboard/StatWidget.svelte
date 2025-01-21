<script lang="ts">
  import { cn } from '$lib/utils';
  import { Icon } from 'svelte-heros-v2';

  let { title, value, change, icon } = $props();

  const formattedValue = $derived(
    new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)
  );

  const changeColor = $derived(
    cn('font-medium', {
      'text-green-500': change && change > 0,
      'text-red-500': change && change < 0,
    })
  );
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
  <div class="flex items-center justify-between">
    <h3 class="text-gray-500 dark:text-gray-400 text-sm font-medium">{title}</h3>
  </div>
  <div class="mt-2">
    <p class="text-3xl font-bold text-gray-900 dark:text-white">
      {formattedValue}
    </p>
    {#if change !== undefined}
      <p class={changeColor}>
        {change > 0 ? '+' : ''}{change}%
      </p>
    {/if}
  </div>
</div>
