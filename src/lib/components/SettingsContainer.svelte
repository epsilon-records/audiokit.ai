<script lang="ts">
  let { title } = $props<{
    title: string;
  }>();
</script>

<div class="space-y-6">
  <div>
    <h3 class="text-2xl font-medium">{title}</h3>
    <div class="text-md text-muted-foreground">
      <slot name="description" />
    </div>
  </div>
  <div class="border border-slate-500 rounded-lg p-4">
    <slot />
  </div>
</div>
