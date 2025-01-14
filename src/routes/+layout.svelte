<script lang="ts">
  import '../app.css';
  import Nav from '$lib/components/Nav.svelte';

  let { children } = $props();
</script>

<Nav />
<div class="min-h-full">
  {@render children()}
</div>
