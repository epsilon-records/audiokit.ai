<script lang="ts">
  import { GlobeAlt } from 'svelte-heros-v2';
  import {
    siSpotify,
    siApplemusic,
    siFacebook,
    siX,
    siInstagram,
    siYoutube,
    siSoundcloud,
    siTiktok,
    siTwitch,
  } from 'simple-icons';
  import type { Artist } from '$lib/types';

  let { artist } = $props<{ artist: Artist }>();

  const socialLinks = $derived(
    Object.entries({
      spotify: { url: artist.spotify, icon: siSpotify },
      apple_music: { url: artist.apple_music, icon: siApplemusic },
      facebook: { url: artist.facebook, icon: siFacebook },
      x: { url: artist.x, icon: siX },
      instagram: { url: artist.instagram, icon: siInstagram },
      youtube: { url: artist.youtube, icon: siYoutube },
      soundcloud: { url: artist.soundcloud, icon: siSoundcloud },
      tiktok: { url: artist.tiktok, icon: siTiktok },
      twitch: { url: artist.twitch, icon: siTwitch },
    })
      .filter(([_, data]) => data.url)
      .map(([platform, data]) => ({
        platform,
        url: data.url as string,
        path: data.icon.path,
      })),
  );
</script>

{#if artist.website || socialLinks.length > 0}
  <div>
    <h2 class="text-sm text-[#00ffff] uppercase mb-2">Follow</h2>
    <div class="flex gap-4">
      {#if artist.website}
        <a
          href={artist.website}
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-2 text-[#ff00ff] hover:text-[#00ffff] transition-colors group"
        >
          <GlobeAlt class="w-5 h-5 transition-transform group-hover:scale-110" />
          <span class="text-sm">website</span>
        </a>
      {/if}
      {#each socialLinks as { platform, url, path }}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-2 text-[#ff00ff] hover:text-[#00ffff] transition-colors group"
        >
          <svg
            role="img"
            viewBox="0 0 24 24"
            class="w-5 h-5 transition-transform group-hover:scale-110"
          >
            <path fill="currentColor" d={path} />
          </svg>
          <span class="text-sm">{platform}</span>
        </a>
      {/each}
    </div>
  </div>
{/if}
