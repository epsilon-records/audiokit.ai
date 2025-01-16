<script lang="ts">
  let {
    title,
    bgColor = 'bg-black',
    textColor = 'text-[#00ff00]',
    children
  } = $props<{
    title?: string;
    bgColor?: string;
    textColor?: string;
    children: () => any;
  }>();
</script>

<div class="min-h-screen py-24 {bgColor}">
  <div class="container mx-auto px-4">
    {#if title}
      <h1 class="text-4xl font-bold {textColor} mb-12">{title}</h1>
    {/if}
    {@render children()}
  </div>
</div>
