<!-- AudioPlayer.svelte -->
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Slider } from '$lib/components/ui/slider';
  import { PlayIcon, PauseIcon, SkipBack, SkipForward } from 'lucide-svelte';
  import WaveSurfer from 'wavesurfer.js';
  import { onMount } from 'svelte';

  let isPlaying = $state(false);
  let audio = $state<HTMLAudioElement | null>(null);
  let currentTime = $state(0);
  let duration = $state(0);
  let waveformRef = $state<HTMLDivElement | null>(null);
  let wavesurfer: WaveSurfer;

  const testTrack = {
    title: 'The Vamp',
    artist: 'Acid Boy',
    coverUrl: 'https://f002.backblazeb2.com/file/epsilon-catalog/Acid+Boy/303:+Part+One/logo.gif',
    audioUrl: '/audio/Acid_Boy_The_Vamp.mp3',
  };

  onMount(() => {
    if (!waveformRef) return;

    wavesurfer = WaveSurfer.create({
      container: waveformRef,
      url: testTrack.audioUrl,
      height: 40,
      waveColor: '#0d9488', // Teal-600
      progressColor: '#0f766e', // Teal-700
      cursorWidth: 0,
      barWidth: 2,
      barGap: 1,
      barRadius: 3,
      normalize: true,
      interact: true,
    });

    wavesurfer.on('ready', () => {
      duration = wavesurfer.getDuration();
    });

    wavesurfer.on('timeupdate', (currentTime) => {
      handleTimeUpdate(currentTime);
    });

    wavesurfer.on('interaction', (position) => {
      currentTime = position;
    });

    return () => {
      wavesurfer.destroy();
    };
  });

  async function togglePlay() {
    try {
      if (isPlaying) {
        wavesurfer.pause();
        isPlaying = false;
      } else {
        await wavesurfer.play();
        isPlaying = true;
      }
    } catch (error) {
      // console.error('Playback error:', error);
      isPlaying = false;
    }
  }

  function formatTime(seconds: number): string {
    if (!isFinite(seconds)) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  function handleTimeUpdate(time: number) {
    currentTime = time;
  }

  function handleSliderChange(value: number[]) {
    const newTime = value[0];
    wavesurfer.setTime(newTime);
    currentTime = newTime;
  }
</script>

<div class="fixed bottom-0 left-0 right-0 bg-background border-t p-4">
  <div class="container mx-auto flex flex-col gap-2">
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <img
          src={testTrack.coverUrl}
          alt={`${testTrack.title} cover`}
          class="h-16 w-16 rounded-md object-cover"
        />
        <div class="flex flex-col">
          <span class="text-sm font-medium">{testTrack.title}</span>
          <span class="text-xs text-muted-foreground">{testTrack.artist}</span>
        </div>
      </div>

      <div class="flex flex-col items-center gap-2 flex-1 px-4">
        <div class="flex items-center gap-2 w-full">
          <span class="text-xs w-12 text-muted-foreground">
            {formatTime(currentTime)}
          </span>

          <div class="flex-1 relative h-10 flex items-center group cursor-pointer">
            <div bind:this={waveformRef} class="absolute inset-0" />
            <Slider
              value={[currentTime]}
              max={duration || 100}
              step={1}
              onvaluechange={handleSliderChange}
              class="opacity-75 group-hover:opacity-100 transition-opacity"
            />
          </div>

          <span class="text-xs w-12 text-muted-foreground">
            {formatTime(duration)}
          </span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <Button variant="ghost" size="icon" class="hover:bg-accent hover:text-accent-foreground">
          <SkipBack class="h-5 w-5" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onclick={togglePlay}
          class="hover:bg-accent hover:text-accent-foreground"
        >
          {#if isPlaying}
            <PauseIcon class="h-6 w-6" />
          {:else}
            <PlayIcon class="h-6 w-6" />
          {/if}
        </Button>

        <Button variant="ghost" size="icon" class="hover:bg-accent hover:text-accent-foreground">
          <SkipForward class="h-5 w-5" />
        </Button>
      </div>
    </div>
  </div>
</div>
