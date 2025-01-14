<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { src = '/default-avatar.jpg', size = 'w-20 h-20' } = $props<{
    src?: string;
    size?: string;
  }>();
</script>

<ImageHandler {src} alt="Profile" class="rounded-full {size}" fallback="/default-avatar.jpg" />
