<script lang="ts">
  let { class: className = '', children } = $props<{
    class?: string;
    children: () => any;
  }>();
</script>

<div class="min-h-screen pt-16 {className}">
  <main class="container mx-auto px-4 py-4 sm:py-6 lg:py-8 max-w-7xl">
    {@render children()}
  </main>
</div>
