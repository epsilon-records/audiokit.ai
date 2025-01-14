<script lang="ts">
  import '../app.css';
  import Nav from '$lib/components/ui/Nav.svelte';
  let { children } = $props();
</script>

<div class="min-h-full">
  <Nav />
  {@render children()}
</div>
