<script lang="ts">
  let { title } = $props<{
    title: string;
  }>();
</script>

<div class="space-y-4">
  <h3 class="text-lg font-semibold">{title}</h3>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {@render children()}
  </div>
</div>
