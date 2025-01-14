<script lang="ts">
  import type { PageData } from './$types';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import ProfileAvatar from '$lib/components/ProfileAvatar.svelte';
  import { Icon, Pencil } from 'svelte-hero-icons';

  let { data } = $props<{ data: PageData }>();
  let previewSrc = $state('https://placeimg.com/80/80/people');

  const showPreview = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const files = target.files;

    if (files?.[0]) {
      previewSrc = URL.createObjectURL(files[0]);
    }
  };
</script>

<SettingsContainer title="Profile">
  <svelte:fragment slot="description">Manage your public profile information.</svelte:fragment>

  <div class="space-y-4">
    <div class="flex items-center gap-4">
      <ProfileAvatar src={previewSrc} />
      <label class="cursor-pointer">
        <input type="file" class="hidden" accept="image/*" onchange={showPreview} />
        <div class="flex items-center gap-2 text-sm text-primary hover:text-primary/80">
          <Icon src={Pencil} class="w-4 h-4" />
          Change Avatar
        </div>
      </label>
    </div>
    <!-- Add other profile fields here -->
  </div>
</SettingsContainer>
