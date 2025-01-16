<script lang="ts">
  let { 
    title,
    children,
    description 
  } = $props<{
    title: string;
    children: () => any;
    description?: () => any;
  }>();
</script>

<div class="container mx-auto px-4 py-24">
  <div class="mb-8">
    <h3 class="text-2xl font-medium">{title}</h3>
    <div class="text-md text-muted-foreground">
      {#if description}
        {@render description()}
      {/if}
    </div>
  </div>
  {@render children()}
</div>
