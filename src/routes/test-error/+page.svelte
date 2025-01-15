<script lang="ts">
  let { data } = $props();
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="text-center space-y-6">
    <h1 class="text-4xl font-bold">Test Success!</h1>
    <p class="text-muted-foreground">{data.message}</p>
    <a href="/test-error" class="btn btn-primary">Try Again</a>
  </div>
</div>
