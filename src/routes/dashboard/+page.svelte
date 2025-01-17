<script lang="ts">
  import { page } from '$app/stores';

  // You can access the error if redirected from a failed verification
  let error = $derived($page.url.searchParams.get('error'));
</script>

{#if error}
  <div class="alert alert-error">
    {error === 'payment-verification-failed'
      ? 'Unable to verify your payment. Please contact support.'
      : 'An error occurred.'}
  </div>
{/if}

<!-- Rest of your dashboard content -->
