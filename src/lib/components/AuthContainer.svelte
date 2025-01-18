<script lang="ts">
  let { title } = $props<{ title: string }>();
</script>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-md mx-auto">
    <h1 class="text-2xl font-bold text-center mb-8">{title}</h1>
    <div class="min-h-[600px] bg-card rounded-lg p-4">
      <slot />
    </div>
  </div>
</div>
