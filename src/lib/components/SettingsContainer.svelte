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
  <slot />
</div>
