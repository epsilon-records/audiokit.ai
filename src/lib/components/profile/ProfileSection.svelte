<script lang="ts">
  import { Icon, Pencil } from 'svelte-hero-icons';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import ImageHandler from '$lib/components/ImageHandler.svelte';
  import { cn } from '$lib/utils';

  let { form } = $props();
  let avatarPreview = $state('');

  function handleAvatarChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        avatarPreview = e.target?.result as string;
      };
      reader.readAsDataURL(input.files[0]);
    }
  }
</script>

<section class="mb-12">
  <h2
    class="text-2xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Artist Profile
  </h2>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Stage Name -->
      <div class="form-control w-full">
        <Field {form} name="stage_name">
          <Control>
            {#snippet children({ props })}
              <Label class="text-base font-medium text-gray-900 dark:text-gray-100"
                >Artist Name</Label
              >
              <input
                {...props}
                class={cn(
                  'mt-1 block w-full rounded-md shadow-sm sm:text-sm',
                  'border-gray-300 focus:border-primary focus:ring-primary',
                  'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
                )}
                bind:value={form.data.stage_name}
              />
            {/snippet}
          </Control>
          <Description>Your public artist name or stage name</Description>
          <FieldErrors />
        </Field>
      </div>

      <!-- Legal Name -->
      <div class="form-control w-full">
        <Field {form} name="legal_name">
          <Control>
            {#snippet children({ props })}
              <Label class="text-base font-medium text-gray-900 dark:text-gray-100"
                >Legal Name</Label
              >
              <input
                {...props}
                class={cn(
                  'mt-1 block w-full rounded-md shadow-sm sm:text-sm',
                  'border-gray-300 focus:border-primary focus:ring-primary',
                  'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
                )}
                bind:value={form.data.legal_name}
              />
            {/snippet}
          </Control>
          <Description>Your legal name (for contracts and payments)</Description>
          <FieldErrors />
        </Field>
      </div>

      <!-- Profile Photo -->
      <div class="form-control w-full">
        <Label class="text-base font-medium text-gray-900 dark:text-gray-100">Profile Photo</Label>
        <div class="mt-1 flex items-center space-x-4">
          <label class="relative cursor-pointer group">
            <div class="w-32 h-32 rounded-full overflow-hidden">
              <ImageHandler
                src={avatarPreview || form.data.avatar_url || '/default-avatar.jpg'}
                alt="Profile photo"
                class="w-full h-full"
              />
            </div>
            <div class="absolute bottom-0 right-0">
              <span
                class="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white hover:bg-primary/90 transition-colors"
              >
                <Icon src={Pencil} class="w-4 h-4" />
              </span>
            </div>
            <input
              type="file"
              class="hidden"
              accept="image/*"
              name="avatar"
              onchange={handleAvatarChange}
            />
          </label>
        </div>
        <Description>Upload a professional photo (recommended size: 400x400px)</Description>
      </div>
    </div>
  </div>
</section>
