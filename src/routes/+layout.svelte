<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import type { Snippet } from 'svelte';
  import { goto } from '$app/navigation';

  let { children } = $props<{ children: Snippet }>();

  // Configure router functions for Clerk
  const routerPush = (to: string) => goto(to);
  const routerReplace = (to: string) => goto(to, { replaceState: true });
</script>

<ClerkProvider
  {routerPush}
  {routerReplace}
  publishableKey={import.meta.env.PUBLIC_CLERK_PUBLISHABLE_KEY}
>
  <Nav />
  {@render children()}
</ClerkProvider>
