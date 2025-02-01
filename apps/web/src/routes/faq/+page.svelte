<script lang="ts">
  import { faqData } from '$lib/data/faq-data';
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { fade, fly } from 'svelte/transition';

  let expandedQuestions = $state(new Set<string>());
  let searchQuery = $state('');

  let filteredFaqData = $derived(
    faqData
      .map((category) => ({
        ...category,
        questions: category.questions.filter(
          (q) =>
            q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            q.answer.toLowerCase().includes(searchQuery.toLowerCase())
        ),
      }))
      .filter((category) => category.questions.length > 0)
  );

  function toggleQuestion(categoryIndex: number, questionIndex: number) {
    const key = `${categoryIndex}-${questionIndex}`;
    expandedQuestions = new Set(expandedQuestions);
    if (expandedQuestions.has(key)) {
      expandedQuestions.delete(key);
    } else {
      expandedQuestions.add(key);
    }
  }
</script>

<svelte:head>
  <title>FAQ - AudioKit Distribution</title>
  <meta
    name="description"
    content="Frequently asked questions about AudioKit music distribution service. Learn about our pricing, platforms, technical requirements, and more."
  />
</svelte:head>

<div class="relative">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="container max-w-4xl mx-auto px-4 py-16 relative z-10">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <div class="bg-white inline-block">
        <h1
          class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
        >
          Frequently Asked Questions
        </h1>
      </div>
      <p class="bg-white text-muted-foreground max-w-2xl mx-auto text-lg">
        Find answers to common questions about our services, pricing, and technical requirements.
      </p>
    </div>

    <div class="mb-8" in:fly={{ y: 20, duration: 600 }}>
      <input
        type="search"
        placeholder="Search FAQ..."
        class="w-full p-3 rounded-lg bg-background border border-input"
        bind:value={searchQuery}
      />
    </div>

    {#each filteredFaqData as category, categoryIndex}
      <div class="mb-12" in:fly={{ y: 20, duration: 600, delay: categoryIndex * 100 }}>
        <h2
          class="text-2xl font-semibold mb-6 text-primary inline-block bg-white px-4 py-2 rounded-lg"
        >
          {category.title}
        </h2>

        <div class="space-y-4">
          {#each category.questions as question, questionIndex}
            <div
              class="border border-border rounded-lg overflow-hidden bg-background/80 backdrop-blur-sm"
            >
              <Button
                variant="ghost"
                class="w-full p-4 flex justify-between items-center text-left"
                onclick={() => toggleQuestion(categoryIndex, questionIndex)}
              >
                <span class="font-medium">{question.question}</span>
                <svg
                  class={cn(
                    'w-5 h-5 transition-transform',
                    expandedQuestions.has(`${categoryIndex}-${questionIndex}`) ? 'rotate-180' : ''
                  )}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </Button>

              {#if expandedQuestions.has(`${categoryIndex}-${questionIndex}`)}
                <div class="p-4 bg-muted/50 border-t border-border">
                  <p class="text-foreground font-medium">{question.answer}</p>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/each}

    {#if filteredFaqData.length === 0}
      <div
        class="text-center py-12 text-muted-foreground bg-background/80 backdrop-blur-sm rounded-lg"
      >
        <p>No FAQ entries found matching your search.</p>
      </div>
    {/if}

    <div class="text-center py-12 rounded-lg" in:fade={{ duration: 800, delay: 200 }}>
      <div class="flex flex-col items-center gap-4">
        <h2 class="bg-white px-6 py-2 rounded-lg text-4xl font-semibold text-primary">
          Still have questions?
        </h2>
        <div class="bg-white px-6 py-2 rounded-lg">
          <p class="text-muted-foreground">Our support team is here to help you succeed.</p>
        </div>
        <div class="flex items-center justify-center gap-4">
          <Button href="/upgrade" variant="default" class="text-lg secondary hover:opacity-90">
            Get Started Now
          </Button>
          <Button href="mailto:support@audiokit.ai" variant="outline" class="text-lg gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            Contact Support
          </Button>
        </div>
      </div>
    </div>
  </div>
</div>
