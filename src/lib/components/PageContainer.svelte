<script lang="ts">
  let {
    title,
    bgColor = 'bg-black',
    textColor = 'text-[#00ff00]',
  } = $props<{
    title?: string;
    bgColor?: string;
    textColor?: string;
  }>();
</script>

<div class="min-h-screen {bgColor}">
  <div class="container mx-auto px-4 pt-32 pb-12">
    {#if title}
      <h1 class="text-4xl font-bold {textColor} mb-12">{title}</h1>
    {/if}
    <slot />
  </div>
</div>
