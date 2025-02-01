<script lang="ts">
  import HeroContainer from '$lib/components/HeroContainer.svelte';
  let displayText = $state('');
  let isTypingDone = $state(false);
  let showStrikethrough = $state(false);

  const fullText = 'Build Better API Solutions';
  const finalText = 'Build Better AI Solutions';

  $effect(() => {
    typeText();
  });

  async function typeText() {
    // Type out the initial text
    for (let i = 0; i < fullText.length; i++) {
      displayText = fullText.slice(0, i + 1);
      await new Promise((resolve) => setTimeout(resolve, 50));
    }

    isTypingDone = true;

    // Wait a moment before starting the replacement
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Show strikethrough on "API"
    showStrikethrough = true;

    await new Promise((resolve) => setTimeout(resolve, 500));

    // Replace "API" with "AI"
    displayText = finalText;
  }
</script>

<svelte:head>
  <title>AudioKit | Music Distribution & Label Services</title>
  <meta name="description" content="Professional music distribution and label services platform" />
</svelte:head>

<HeroContainer />
