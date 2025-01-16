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

  // Configure router functions for Clerk
  const routerPush = (to: string) => goto(to);
  const routerReplace = (to: string) => goto(to, { replaceState: true });

  // Set initial demo track on client-side only
  $effect(() => {
    if (typeof window !== 'undefined') {
      audioStore.playTrack({
        id: 'demo-1',
        title: 'Welcome to Epsilon',
        artist: 'Epsilon Records',
        coverArt: '/demo-cover.jpg',
        audioUrl: '/demo-track.mp3'
      });
    }
  });
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
  <AudioPlayer />
</ClerkProvider>
