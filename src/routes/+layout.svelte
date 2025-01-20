<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Toaster } from 'svelte-sonner';
  import type { Snippet } from 'svelte';
  import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';

  let { children } = $props<{ children: Snippet }>();
</script>

<ClerkProvider publishableKey={PUBLIC_CLERK_PUBLISHABLE_KEY}>
  <div class="min-h-screen flex flex-col">
    <Nav />
    <main class="flex-1 pt-16">
      {@render children()}
    </main>
    <Footer />
  </div>
  <Toaster richColors />
</ClerkProvider>
