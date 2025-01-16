<script lang="ts">
  let { 
    title,
    children 
  } = $props<{
    title: string;
    children: () => any;
  }>();
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="m-4">
    <h1 class="text-2xl font-bold mb-4 text-center">{title}</h1>
    {@render children()}
  </div>
</div>
