<script lang="ts">
  import { ExclamationCircle } from 'svelte-heros-v2';

  let {
    src,
    alt,
    fallback = '/default-image.jpg',
    class: className = '',
    aspectRatio = 'aspect-square',
    objectFit = 'object-cover',
    enableZoom = true,
  } = $props<{
    src: string;
    alt: string;
    fallback?: string;
    class?: string;
    aspectRatio?: string;
    objectFit?: string;
    enableZoom?: boolean;
  }>();

  let error = $state(false);
  let loading = $state(true);
  let imageSrc = $derived(error ? fallback : src);

  function handleError() {
    error = true;
    loading = false;
  }

  function handleLoad() {
    loading = false;
  }
</script>

<div class="{aspectRatio} relative overflow-hidden {className}">
  {#if loading}
    <div class="absolute inset-0 bg-muted animate-pulse"></div>
  {/if}

  <img
    {alt}
    src={imageSrc}
    onerror={handleError}
    onload={handleLoad}
    class="w-full h-full transition-transform duration-300 {objectFit}
      {loading ? 'opacity-0' : 'opacity-100'}
      {enableZoom ? 'group-hover:scale-105' : ''}"
  />

  {#if error}
    <div class="absolute inset-0 flex items-center justify-center bg-muted/50">
      <ExclamationCircle class="w-8 h-8 text-muted-foreground" />
    </div>
  {/if}
</div>
