<script lang="ts">
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';

  let { form } = $props();

  const socialPlatforms = [
    { name: 'instagram_handle', label: 'Instagram', placeholder: '@username' },
    { name: 'twitter_handle', label: 'Twitter', placeholder: '@username' },
    { name: 'facebook_url', label: 'Facebook', placeholder: 'Profile URL' },
    { name: 'youtube_url', label: 'YouTube', placeholder: 'Channel URL' },
  ];
</script>

<section class="mb-12">
  <h2
    class="text-2xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Social Media
  </h2>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {#each socialPlatforms as platform}
        <div class="form-control w-full">
          <Field {form} name={platform.name}>
            <Control>
              {#snippet children({ props })}
                <Label class="text-base font-medium text-gray-900 dark:text-gray-100">
                  {platform.label}
                </Label>
                <input
                  {...props}
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder={platform.placeholder}
                  bind:value={form.data[platform.name]}
                />
              {/snippet}
            </Control>
            <Description>Your {platform.label} profile</Description>
            <FieldErrors />
          </Field>
        </div>
      {/each}
    </div>
  </div>
</section>
