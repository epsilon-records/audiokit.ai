<script lang="ts">
  import PricingPage from '$lib/components/PricingPage.svelte';

  let { data } = $props();
  let email = null;
  let title = $derived(data.title);
  let description = $derived(data.description);
</script>

<PricingPage {email} {title} {description} />
