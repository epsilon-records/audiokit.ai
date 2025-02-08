<script lang="ts">
  import { page } from '$app/stores';

  let errorMessage = $derived(
    $page.status === 404
      ? "The page you're looking for doesn't exist."
      : 'Something went wrong on our end.'
  );
</script>

<div class="min-h-screen flex items-start justify-center relative pt-24">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>

  <div class="text-center space-y-6 relative z-10 bg-white p-8 rounded-lg shadow-lg">
    <h1 class="text-4xl font-bold">{$page.status}: {$page.error?.message}</h1>
    <p class="text-muted-foreground">{errorMessage}</p>
    <a href="/" class="btn btn-primary">Go Home</a>
  </div>
</div>
