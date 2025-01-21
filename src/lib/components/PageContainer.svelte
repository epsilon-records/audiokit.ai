<script lang="ts">
  let {
    title,
    bgColor = 'bg-background',
    textColor = 'text-foreground',
    children,
  } = $props<{
    title: string;
    bgColor?: string;
    textColor?: string;
    children: () => any;
  }>();
</script>

<div class="min-h-screen pt-16 {bgColor}">
  <div class="container mx-auto px-4 py-6 sm:py-8 lg:py-12 max-w-7xl">
    <h1 class="text-3xl sm:text-4xl font-bold mb-6 sm:mb-8 lg:mb-12 {textColor}">{title}</h1>
    {@render children()}
  </div>
</div>
