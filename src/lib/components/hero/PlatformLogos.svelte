<script lang="ts">
  import {
    siSpotify,
    siApplemusic,
    siYoutubemusic,
    siSoundcloud,
    siBandcamp,
    siTidal,
    siAmazonmusic,
    siPandora,
    siTiktok,
    siInstagram,
    siX,
    siTwitch,
  } from 'simple-icons';

  interface Props {
    ANIMATION_BASE_DELAY: number;
  }
  let { ANIMATION_BASE_DELAY } = $props<Props>();
</script>

<div
  in:fade={{ duration: 1000, delay: ANIMATION_BASE_DELAY + 600 }}
  class="w-full max-w-xl space-y-6 pt-8 border-t border-border/40"
>
  <p class="text-sm text-muted-foreground">Available on all major platforms</p>
  <div
    class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4 md:gap-6 items-center justify-items-center"
  >
    {#each [{ icon: siSpotify, color: '#1DB954' }, { icon: siApplemusic, color: '#FA243C' }, { icon: siYoutubemusic, color: '#FF0000' }, { icon: siTidal, color: '#000000' }, { icon: siAmazonmusic, color: '#FF9900' }, { icon: siSoundcloud, color: '#FF6B00' }, { icon: siBandcamp, color: '#629AA9' }, { icon: siPandora, color: '#00A4DC' }, { icon: siTiktok, color: '#000000' }, { icon: siInstagram, color: '#E4405F' }, { icon: siX, color: '#000000' }, { icon: siTwitch, color: '#9146FF' }] as item}
      <svg
        class="w-8 h-8 md:w-10 md:h-10 transition-all duration-300 hover:scale-110"
        style="color: {item.color}"
        viewBox="0 0 24 24"
      >
        <path fill="currentColor" d={item.icon.path} />
      </svg>
    {/each}
  </div>
</div>
