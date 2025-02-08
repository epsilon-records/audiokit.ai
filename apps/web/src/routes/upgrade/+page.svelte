<script lang="ts">
  import PricingPage from '$lib/components/PricingPage.svelte';

  let { data } = $props();
  let auth = $derived(data.auth);
  let title = $derived(data.title);
  let description = $derived(data.description);
</script>

<PricingPage {auth} {title} {description} />
