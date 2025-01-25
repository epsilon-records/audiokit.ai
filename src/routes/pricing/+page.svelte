<script lang="ts">
  import PricingPage from '$lib/components/PricingPage.svelte';

  let { data } = $props();
  let auth = null;
  let title = $derived(data.title);
  let description = $derived(data.description);
</script>

<PricingPage {auth} {title} {description} />
