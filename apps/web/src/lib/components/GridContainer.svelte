<script lang="ts">
  let { cols = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3', children } = $props<{
    cols?: string;
    children: () => any;
  }>();
</script>

<div class="grid {cols} gap-8">
  {@render children()}
</div>
