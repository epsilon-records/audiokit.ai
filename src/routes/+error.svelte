<script lang="ts">
  import { page } from '$app/stores';

  let errorMessage = $derived(
    $page.status === 404
      ? "The page you're looking for doesn't exist."
      : 'Something went wrong on our end.',
  );
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="text-center space-y-6">
    <h1 class="text-4xl font-bold">{$page.status}: {$page.error?.message}</h1>
    <p class="text-muted-foreground">{errorMessage}</p>
    <a href="/" class="btn btn-primary">Go Home</a>
  </div>
</div>
