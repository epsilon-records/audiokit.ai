<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';

  let { children } = $props();
</script>

<ClerkProvider>
  <Nav />
  {@render children()}
</ClerkProvider>
