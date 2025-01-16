<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import AudioPlayer from '$lib/components/AudioPlayer.svelte';
  import { audioStore } from '$lib/stores/audioStore.svelte';
  import type { Snippet } from 'svelte';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let { children } = $props<{ children: Snippet }>();

  // Configure router functions for Clerk
  const routerPush = (to: string) => goto(to);
  const routerReplace = (to: string) => goto(to, { replaceState: true });

  // Set initial demo track only once on mount
  onMount(() => {
    audioStore.playTrack({
      id: 'demo-1',
      title: 'The Vamp',
      artist: 'Acid Boy',
      coverArt: 'https://f002.backblazeb2.com/file/epsilon-catalog/Acid+Boy/303:+Part+One/logo.gif',
      audioUrl: '/audio/Acid_Boy_The_Vamp.mp3',
    });
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
  <!-- <AudioPlayer /> -->
</ClerkProvider>
