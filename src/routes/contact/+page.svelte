<script lang="ts">
  import { fade, fly, scale } from 'svelte/transition';
  import { Mail, MessageSquare, Clock, ExternalLink } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Contact | AudioKit</title>
  <meta name="description" content="Get in touch with the AudioKit team" />
</svelte:head>

<div class="relative min-h-[80vh] flex items-center">
  <div class="container max-w-4xl mx-auto px-4 py-16">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <div class="text-4xl mb-4" in:scale={{ duration: 600, delay: 200 }}>👋</div>
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
      class="bg-gradient-to-br from-primary/5 to-blue-500/5 backdrop-blur-sm rounded-xl border border-border/40 p-12 text-center hover:shadow-lg transition-all duration-300"
    >
      <h2 class="text-2xl font-bold mb-4">Email Us ✉️</h2>
      <div class="flex items-center justify-center gap-2 mb-6 text-muted-foreground">
        <Clock class="w-4 h-4" />
        <p>Our support team typically responds within 24 hours during business days.</p>
      </div>

      <a
        href="mailto:support@audiokit.ai"
        class="group inline-flex items-center text-2xl font-medium text-primary hover:text-primary/80 transition-colors"
      >
        support@audiokit.ai
        <ExternalLink class="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" />
      </a>
    </div>

    <div class="mt-16 text-center space-y-4" in:fade={{ duration: 800, delay: 400 }}>
      <div class="text-3xl mb-2" in:scale={{ duration: 600, delay: 600 }}>🤔</div>
      <h3 class="text-xl font-semibold mb-4">Looking for immediate answers?</h3>
      <p class="text-muted-foreground mb-6">
        Check out our comprehensive FAQ section for quick solutions to common questions.
      </p>
      <a
        href="/faq"
        class="group inline-flex items-center justify-center px-8 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 hover:scale-105"
      >
        <MessageSquare class="w-5 h-5 mr-2" />
        Visit FAQ
        <span class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">→</span>
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
