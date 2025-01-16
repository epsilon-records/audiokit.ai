<!-- AudioPlayer.svelte -->
<script lang="ts">
  import { audioStore } from '$lib/stores/audioStore';
  import { Button } from '$lib/components/ui/button';
  import { Slider } from '$lib/components/ui/slider';
  import { PlayIcon, PauseIcon } from 'lucide-svelte';

  let isPlaying = $state(false);
  let currentTime = $state(0);
  let duration = $state(0);
  let audio = $state<HTMLAudioElement | null>(null);

  // Get current track from store using $derived
  let currentTrack = $derived(audioStore.currentTrack);

  // Only run audio-related effects on the client side
  $effect(() => {
    if (typeof window === 'undefined') return;
    
    if (currentTrack && audio) {
      audio.src = currentTrack.audioUrl;
      audio.load();
      duration = audio.duration;
    }
  });

  function togglePlay() {
    if (!audio) return;
    
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    isPlaying = !isPlaying;
  }

  function handleTimeUpdate() {
    if (!audio) return;
    currentTime = audio.currentTime;
    duration = audio.duration;
  }

  function handleSliderChange(value: number[]) {
    if (!audio) return;
    audio.currentTime = value[0];
  }
</script>

{#if currentTrack}
  <div class="fixed bottom-0 left-0 right-0 bg-background border-t p-4">
    <audio
      bind:this={audio}
      on:timeupdate={handleTimeUpdate}
      on:ended={() => (isPlaying = false)}
    />
    
    <div class="container mx-auto flex items-center gap-4">
      <img
        src={currentTrack.coverArt}
        alt={currentTrack.title}
        class="w-12 h-12 rounded"
      />
      
      <div class="flex-1">
        <h3 class="font-medium">{currentTrack.title}</h3>
        <p class="text-sm text-muted-foreground">{currentTrack.artist}</p>
      </div>

      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" on:click={togglePlay}>
          {#if isPlaying}
            <PauseIcon class="h-6 w-6" />
          {:else}
            <PlayIcon class="h-6 w-6" />
          {/if}
        </Button>

        <div class="w-64">
          <Slider
            value={[currentTime]}
            min={0}
            max={duration || 100}
            step={1}
            onValueChange={handleSliderChange}
          />
        </div>
      </div>
    </div>
  </div>
{/if} 