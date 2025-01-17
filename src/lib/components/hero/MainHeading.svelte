<script lang="ts">
  import Typewriter from 'typewriter-effect/dist/core';
  import { onMount } from 'svelte';

  let elementRef: HTMLHeadingElement;

  onMount(() => {
    const typewriter = new Typewriter(elementRef, {
      delay: 50,
      cursor: '|',
    });

    typewriter
      .typeString('Music Distribution')
      .pauseFor(500)
      .typeString('<br>For The API Era')
      .pauseFor(1000)
      .deleteChars(7)
      .typeString('AI Era')
      .start();
  });
</script>

<h1
  bind:this={elementRef}
  class="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
/>

<style>
  :global(.Typewriter__cursor) {
    @apply text-primary;
  }
</style>
