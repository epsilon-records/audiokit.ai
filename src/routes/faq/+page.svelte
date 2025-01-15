<script lang="ts">
  import { faqData } from '$lib/data/faq-data';
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';

  let expandedQuestions = $state(new Set<string>());
  let searchQuery = $state('');

  let filteredFaqData = $derived(
    faqData
      .map((category) => ({
        ...category,
        questions: category.questions.filter(
          (q) =>
            q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            q.answer.toLowerCase().includes(searchQuery.toLowerCase()),
        ),
      }))
      .filter((category) => category.questions.length > 0),
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
  <title>FAQ - Epsilon Distribution</title>
  <meta
    name="description"
    content="Frequently asked questions about Epsilon music distribution service. Learn about our pricing, platforms, technical requirements, and more."
  />
</svelte:head>

<div class="container mx-auto px-4 py-24 max-w-4xl">
  <h1 class="text-4xl font-bold mb-8 text-primary">Frequently Asked Questions</h1>

  <div class="mb-8">
    <input
      type="search"
      placeholder="Search FAQ..."
      class="w-full p-3 rounded-lg bg-background border border-input"
      bind:value={searchQuery}
    />
  </div>

  {#each filteredFaqData as category, categoryIndex}
    <div class="mb-12">
      <h2 class="text-2xl font-semibold mb-6 text-primary">{category.title}</h2>

      <div class="space-y-4">
        {#each category.questions as question, questionIndex}
          <div class="border border-border rounded-lg overflow-hidden">
            <Button
              variant="ghost"
              class="w-full p-4 flex justify-between items-center text-left"
              onclick={() => toggleQuestion(categoryIndex, questionIndex)}
            >
              <span class="font-medium">{question.question}</span>
              <svg
                class={cn(
                  'w-5 h-5 transition-transform',
                  expandedQuestions.has(`${categoryIndex}-${questionIndex}`) ? 'rotate-180' : '',
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
                <p class="text-muted-foreground">{question.answer}</p>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/each}

  {#if filteredFaqData.length === 0}
    <div class="text-center py-12 text-muted-foreground">
      <p>No FAQ entries found matching your search.</p>
    </div>
  {/if}
</div>

<style lang="postcss">
  /* Add any custom styles here */
</style>
