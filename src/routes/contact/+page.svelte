<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import ContactInfo from '$lib/components/ContactInfo.svelte';
</script>

<PageContainer title="Contact" bgColor="bg-black" textColor="text-[#00ff00]">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
    <ContactForm />
    <ContactInfo />
  </div>
</PageContainer>
