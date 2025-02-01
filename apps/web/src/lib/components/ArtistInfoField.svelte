<script lang="ts">
  let { label, value } = $props<{ label: string; value: string }>();
</script>

{#if value}
  <div>
    <h2 class="text-sm text-[#00ffff] uppercase mb-1">{label}</h2>
    {#if label === 'Biography'}
      <div class="text-lg text-[#00ff00]">{@html value}</div>
    {:else}
      <p class="text-lg text-[#00ff00]">{value}</p>
    {/if}
  </div>
{/if}
