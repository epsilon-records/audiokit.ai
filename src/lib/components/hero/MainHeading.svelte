<script lang="ts">
  import Typewriter from 'typewriter-effect/dist/core';
  import { fade } from 'svelte/transition';

  interface TypewriterOptions {
    delay: number;
    cursor: string;
    cursorClassName?: string;
  }

  let elementRef = $state<HTMLHeadingElement | null>(null);
  let {
    options = {
      delay: 50,
      cursor: '|',
      cursorClassName: 'text-primary',
    },
  } = $props<{ options?: TypewriterOptions }>();

  $effect(() => {
    if (!elementRef) return;

    const typewriter = new Typewriter(elementRef, options);

    typewriter
      .typeString('Label Services')
      .pauseFor(500)
      .typeString('<br>For The API Era')
      .pauseFor(1000)
      .deleteChars(7)
      .typeString('AI Era')
      .start();

    // Cleanup typewriter on component unmount
    return () => {
      typewriter.stop();
    };
  });
</script>

<div class="space-y-4">
  <h1
    bind:this={elementRef}
    in:fade={{ duration: 1000, delay: 200 }}
    class="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Label Services<br />For The API Era
  </h1>

  <p
    in:fade={{ duration: 1000, delay: 400 }}
    class="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto"
  >
    Streamline your music distribution with powerful APIs and AI-driven tools
  </p>
</div>

<style lang="postcss">
  :global(.Typewriter__cursor) {
    @apply text-primary;
  }
</style>
