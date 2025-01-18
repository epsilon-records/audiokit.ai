<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Toaster } from 'svelte-sonner';
  import type { Snippet } from 'svelte';
  import { goto } from '$app/navigation';
  import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';
  import { ModeWatcher } from 'mode-watcher';

  let { children } = $props<{ children: Snippet }>();

  const routerPush = (to: string) => goto(to);
  const routerReplace = (to: string) => goto(to, { replaceState: true });
</script>

<ClerkProvider {routerPush} {routerReplace} publishableKey={PUBLIC_CLERK_PUBLISHABLE_KEY}>
  <ModeWatcher />
  <div class="min-h-screen flex flex-col">
    <Nav />
    <main class="flex-1 pt-16">
      {@render children()}
    </main>
    <Footer />
  </div>
  <Toaster richColors />
</ClerkProvider>
