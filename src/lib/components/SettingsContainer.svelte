<script lang="ts">
  let { title } = $props<{
    title: string;
  }>();
</script>

<div class="container mx-auto px-4 py-24">
  <div class="mb-8">
    <h3 class="text-2xl font-medium">{title}</h3>
    <div class="text-md text-muted-foreground">
      {@render description()}
    </div>
  </div>
  {@render children()}
</div>
