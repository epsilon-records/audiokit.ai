<script lang="ts">
  import PricingPage from '$lib/components/PricingPage.svelte';

  let { data } = $props();
  let email = $derived(data.email);
</script>

<PricingPage {email} />
