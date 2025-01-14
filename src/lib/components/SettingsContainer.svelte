<script lang="ts">
  let { title } = $props<{
    title: string;
  }>();
</script>

<div class="space-y-6">
  <div>
    <h3 class="text-lg font-medium">{title}</h3>
    <div class="text-sm text-muted-foreground">
      <slot name="description" />
    </div>
  </div>
  <div class="border rounded-lg p-4">
    <slot />
  </div>
</div>
