<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { Mail } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Contact | AudioKit</title>
  <meta name="description" content="Get in touch with the AudioKit team" />
</svelte:head>

<div class="relative min-h-[80vh] flex items-center">
  <div class="container max-w-4xl mx-auto px-4 py-16">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <h1
        class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
      >
        Get in Touch
      </h1>
      <p class="text-muted-foreground max-w-2xl mx-auto text-lg">
        We're here to help you succeed in your music career. Reach out to us for support, questions,
        or partnership opportunities.
      </p>
    </div>

    <div
      in:fly={{ y: 20, duration: 600, delay: 200 }}
      class="bg-gradient-to-br from-primary/5 to-blue-500/5 backdrop-blur-sm rounded-xl border border-border/40 p-12 text-center"
    >
      <div
        class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-6"
      >
        <Mail class="w-8 h-8 text-primary" />
      </div>

      <h2 class="text-2xl font-bold mb-4">Email Us</h2>
      <p class="text-muted-foreground mb-6">
        Our support team typically responds within 24 hours during business days.
      </p>

      <a
        href="mailto:support@audiokit.ai"
        class="inline-flex items-center text-2xl font-medium text-primary hover:text-primary/80 transition-colors"
      >
        support@audiokit.ai
      </a>
    </div>

    <div class="mt-16 text-center" in:fade={{ duration: 800, delay: 400 }}>
      <h3 class="text-xl font-semibold mb-4">Looking for immediate answers?</h3>
      <p class="text-muted-foreground mb-6">
        Check out our comprehensive FAQ section for quick solutions to common questions.
      </p>
      <a
        href="/faq"
        class="inline-flex items-center justify-center px-8 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        Visit FAQ
      </a>
    </div>
  </div>

  <div
    class="absolute inset-0 -z-10 h-full w-full bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  />
  <div
    class="absolute inset-0 -z-10 h-full w-full bg-gradient-to-br from-primary/5 via-blue-500/5 to-violet-500/5 opacity-50"
  />
</div>
