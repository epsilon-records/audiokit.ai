<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
  import { Wand2, ImagePlus, Mic, Music2, Sliders } from 'lucide-svelte';
  import { fly } from 'svelte/transition';

  interface Tool {
    title: string;
    description: string;
    icon: any;
    href: string;
    comingSoon?: boolean;
    gradient: string;
  }

  const tools: Tool[] = [
    {
      title: 'AI Cover Art Generator',
      description: 'Create unique album artwork using advanced AI image generation',
      icon: ImagePlus,
      href: '/dashboard/tools/cover-art',
      gradient: 'from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900',
    },
    {
      title: 'AI Lyrics Generator',
      description: 'Generate creative lyrics and song ideas with AI assistance',
      icon: Mic,
      href: '/dashboard/tools/lyrics',
      gradient: 'from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900',
    },
    {
      title: 'Track Title Generator',
      description: 'Generate unique and engaging titles for your tracks and albums',
      icon: Music2,
      href: '/dashboard/tools/titles',
      gradient: 'from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900',
    },
    {
      title: 'AI Track Mastering',
      description: 'Professional-grade mastering powered by artificial intelligence',
      icon: Sliders,
      href: '/dashboard/tools/mastering',
      comingSoon: true,
      gradient: 'from-cyan-50 to-cyan-100 dark:from-cyan-950 dark:to-cyan-900',
    },
  ];
</script>

<svelte:head>
  <title>Creative Tools | AudioKit</title>
  <meta name="description" content="AI-powered creative tools for music production and promotion" />
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Creative Tools</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Enhance your creative process with our AI-powered tools and utilities.
    </p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {#each tools as tool, i}
      <div in:fly={{ y: 20, duration: 400, delay: i * 100 }}>
        <Card
          class="flex flex-col h-full transition-all duration-200 hover:shadow-lg hover:scale-[1.02]"
        >
          <CardHeader class="bg-gradient-to-br {tool.gradient} pb-6">
            <div class="flex items-center justify-between">
              <CardTitle class="flex items-center gap-2">
                <svelte:component this={tool.icon} class="h-5 w-5" />
                {tool.title}
              </CardTitle>
              {#if tool.comingSoon}
                <span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                  Coming Soon
                </span>
              {/if}
            </div>
          </CardHeader>
          <CardContent class="flex flex-col flex-1 pt-6">
            <p class="text-muted-foreground">{tool.description}</p>
            <div class="flex-1 flex items-end pt-6">
              <Button
                href={tool.href}
                class="w-full"
                disabled={tool.comingSoon}
                variant={tool.comingSoon ? 'outline' : 'default'}
              >
                <Wand2 class="mr-2 h-4 w-4" />
                {tool.comingSoon ? 'Coming Soon' : 'Launch Tool'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    {/each}
  </div>

  <div
    class="mt-12 p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900 rounded-lg"
  >
    <div class="text-center">
      <h2 class="text-2xl font-bold mb-2">Need a Custom Tool?</h2>
      <p class="text-muted-foreground mb-4">
        We're constantly adding new AI-powered tools. Let us know what would help your creative
        process.
      </p>
      <Button variant="outline" href="mailto:support@audiokit.com">Request a Feature</Button>
    </div>
  </div>
</div>
