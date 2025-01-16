<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import AudioPlayer from '$lib/components/AudioPlayer.svelte';
  import { audioStore } from '$lib/stores/audioStore.svelte';
  import type { Snippet } from 'svelte';
  import { goto } from '$app/navigation';

  let { children } = $props<{ children: Snippet }>();

  const routerPush = (to: string) => goto(to);
  const routerReplace = (to: string) => goto(to, { replaceState: true });
</script>

<ClerkProvider
  {routerPush}
  {routerReplace}
  publishableKey={import.meta.env.PUBLIC_CLERK_PUBLISHABLE_KEY}
>
  <Nav />
  <main class="min-h-[calc(100vh-64px)]">
    {@render children()}
  </main>
  <Footer />
  <!-- <AudioPlayer /> -->
</ClerkProvider>
