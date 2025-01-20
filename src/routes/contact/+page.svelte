<script lang="ts">
  import { fade, fly, scale } from 'svelte/transition';
  import { MessageSquare, Clock, ExternalLink } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Contact | AudioKit</title>
  <meta name="description" content="Get in touch with the AudioKit team" />
</svelte:head>

<div class="relative min-h-[80vh] flex items-center">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="container max-w-4xl mx-auto px-4 py-16 relative z-10">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <h1
        class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
      >
        Get in Touch
      </h1>
      <p
        class="text-muted-foreground max-w-2xl mx-auto text-lg bg-background/50 backdrop-blur-sm rounded-full px-4 py-2 inline-block"
      >
        Reach out to us for support, questions, or partnership opportunities.
      </p>
    </div>

    <div
      in:fly={{ y: 20, duration: 600, delay: 400 }}
      class="relative overflow-hidden rounded-xl border border-border/40 bg-gradient-to-br from-violet-50 via-slate-50 to-indigo-50 dark:from-violet-950/50 dark:via-slate-950/50 dark:to-indigo-950/50 p-12 text-center hover:shadow-lg transition-all duration-300"
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

    <div
      class="mt-8 relative overflow-hidden rounded-xl border border-border/40 bg-gradient-to-br from-emerald-50 via-slate-50 to-teal-50 dark:from-emerald-950/50 dark:via-slate-950/50 dark:to-teal-950/50 p-12 text-center hover:shadow-lg transition-all duration-300"
      in:fade={{ duration: 800, delay: 400 }}
    >
      <div class="text-3xl mb-2" in:scale={{ duration: 600, delay: 600 }}>🤔</div>
      <h3 class="text-xl font-semibold mb-4">Looking for immediate answers?</h3>
      <p class="text-muted-foreground mb-6">
        Check out our comprehensive FAQ section and API documentation for quick solutions to common
        questions.
      </p>
      <div class="flex items-center justify-center gap-4">
        <a href="/faq" class="btn btn-primary inline-flex items-center justify-center gap-2">
          <MessageSquare class="w-5 h-5" />
          Visit FAQ →
        </a>
        <a href="/docs" class="btn btn-secondary gap-4">
          <ExternalLink class="w-5 h-5" />
          View Docs →
        </a>
      </div>
    </div>
  </div>

  <div class="relative">
    <div
      class="absolute inset-0 -z-10 h-full w-full bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
    />
    <div
      class="absolute inset-0 -z-20 h-full w-full bg-gradient-to-br from-primary/5 via-blue-500/5 to-violet-500/5 opacity-50"
    />
  </div>
</div>
