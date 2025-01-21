<script lang="ts">
  import { fly } from 'svelte/transition';
  import { Button } from '$lib/components/ui/button';

  const { ANIMATION_BASE_DELAY } = $props();
</script>

<div
  in:fly={{ y: 30, duration: 800, delay: ANIMATION_BASE_DELAY + 200 }}
  class="flex flex-col sm:flex-row gap-4"
>
  <Button size="lg" class="text-lg px-8" href="/sign-up">Get Started</Button>
  <Button size="lg" variant="outline" class="text-lg px-8" href="/services">Learn More</Button>
</div>
