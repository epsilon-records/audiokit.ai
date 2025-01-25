<script lang="ts">
  import PricingPage from '$lib/components/PricingPage.svelte';

  let { data } = $props();
  let email = $derived(data.auth.email);
  let title = $derived(data.title);
  let description = $derived(data.description);
</script>

<PricingPage {email} {title} {description} />
