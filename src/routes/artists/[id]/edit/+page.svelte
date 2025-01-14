<script lang="ts">
  import { superForm } from 'sveltekit-superforms/client';
  import { Button } from '$lib/components/ui/button';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import FormSection from '$lib/components/FormSection.svelte';
  import FormField from '$lib/components/FormField.svelte';
  import TextareaField from '$lib/components/TextareaField.svelte';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import {
    musicPlatforms,
    socialPlatforms,
    eventPlatforms,
    hiddenArtistFields,
  } from '$lib/config/platforms';
  import type { PageData } from './$types';

  let { data } = $props();
  const { form, errors, enhance } = superForm(data.form);
</script>

<PageContainer>
  <Card class="max-w-3xl mx-auto bg-card">
    <CardHeader>
      <CardTitle>Edit Artist Profile</CardTitle>
    </CardHeader>
    <CardContent>
      <form method="POST" use:enhance class="space-y-8">
        {#each hiddenArtistFields as field}
          <input type="hidden" name={field} bind:value={$form[field]} />
        {/each}

        <FormSection title="Essential Information">
          <FormField
            label="Stage Name"
            id="stage_name"
            bind:value={$form.stage_name}
            error={$errors.stage_name}
            required
          />
          <TextareaField
            label="Biography"
            id="biography"
            bind:value={$form.biography}
            error={$errors.biography}
          />
        </FormSection>

        {#each [{ title: 'Music Platforms', platforms: musicPlatforms }, { title: 'Social Media', platforms: socialPlatforms }, { title: 'Event Platforms', platforms: eventPlatforms }] as section}
          <FormSection title={section.title}>
            {#each section.platforms as platform}
              <FormField
                label={platform.label}
                id={platform.id}
                bind:value={$form[platform.id]}
                placeholder={platform.placeholder}
              />
            {/each}
          </FormSection>
        {/each}

        <div class="flex justify-end gap-4 pt-6">
          <Button variant="outline" href="/artists">Cancel</Button>
          <Button type="submit">Save Changes</Button>
        </div>
      </form>
    </CardContent>
  </Card>
</PageContainer>
