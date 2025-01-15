<script lang="ts">
  import { enhance, applyAction } from '$app/forms';
  import { invalidateAll } from '$app/navigation';
  import { Icon, Pencil } from 'svelte-hero-icons';
  import Input from '$lib/components/Input.svelte';
  import { getImageURL } from '$lib/utils';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import Editor from '$lib/components/Editor.svelte';
  import { countries } from '$lib/data/countries';
  import type { Artist } from '$lib/types/artist';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';

  let { data } = $props<{ data: { user: Artist } }>();
  let loading = $state(false);
  let errors = $state<Record<string, string>>({});

  // Form validation
  const validateForm = (formData: FormData): boolean => {
    errors = {};

    // Required fields validation
    const stage_name = formData.get('stage_name') as string;
    const legal_name = formData.get('legal_name') as string;
    const email = formData.get('email') as string;

    if (!stage_name?.trim()) {
      errors.stage_name = 'Stage name is required';
    }

    if (!legal_name?.trim()) {
      errors.legal_name = 'Legal name is required';
    }

    if (!email?.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email format';
    }

    // URL validations
    const urlFields = [
      'website',
      'spotify',
      'apple_music',
      'bandcamp',
      'mixcloud',
      'snapchat',
      'twitch',
      'youtube',
      'instagram',
      'facebook',
      'x',
      'tiktok',
      'soundcloud',
      'songkick',
      'bandsintown',
      'linkedin',
    ];

    urlFields.forEach((field) => {
      const value = formData.get(field) as string;
      if (value && !value.startsWith('https://')) {
        errors[field] = 'URL must start with https://';
      }
    });

    return Object.keys(errors).length === 0;
  };

  const showPreview = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const files = target.files;

    if (files && files.length > 0) {
      const src = URL.createObjectURL(files[0]);
      const preview = document.querySelector<HTMLImageElement>('#avatar-preview');
      if (preview) {
        preview.src = src;
      }
    }
  };

  const submitUpdateProfile = () => {
    loading = true;
    return async ({ form, result }: { form: HTMLFormElement; result: any }) => {
      const formData = new FormData(form);

      if (!validateForm(formData)) {
        loading = false;
        return;
      }

      switch (result.type) {
        case 'success':
          await invalidateAll();
          break;
        case 'error':
          // Handle specific error cases
          if (result.status === 400) {
            errors = result.data?.errors || { form: 'Invalid form data' };
          }
          break;
        default:
          await applyAction(result);
      }
      loading = false;
    };
  };
</script>

<SettingsContainer title="Artist Profile">
  <svelte:fragment slot="description">
    Manage your profile information, press photos, and social media presence.
  </svelte:fragment>

  <form
    action="?/updateProfile"
    method="POST"
    class="flex flex-col space-y-6 w-full"
    enctype="multipart/form-data"
    use:enhance={submitUpdateProfile}
  >
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Select Artist</h3>
      <p class="text-muted-foreground">
        Choose the artist profile you want to edit. You can switch between different artists or
        create a new artist profile.
      </p>
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/my/settings/profile"
        afterSelectOrganizationUrl="/my/settings/profile"
      />
    </div>

    <!-- Basic Information Section -->
    <div class="divider divider-accent text-xl pt-4">Basic Information</div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Input
        id="stage_name"
        label="Artist Name"
        value={data?.user?.stage_name}
        required
        disabled={loading}
      />
      <!-- Artist Photos -->
      <div class="form-control w-full max-w-lg">
        <label for="avatar" class="label font-medium pb-1">
          <span class="label-text text-lg">Artist Photo</span>
        </label>
        <label for="avatar" class="avatar w-32 rounded-full hover:cursor-pointer">
          <label for="avatar" class="absolute -bottom-0.5 -right-0.5 hover:cursor-pointer">
            <span class="btn btn-circle btn-sm btn-secondary">
              <Icon src={Pencil} class="w-4 h-4" />
            </span>
          </label>
          <div class="w-32">
            <img
              src={data.user?.avatar
                ? getImageURL(data.user?.collectionId, data.user?.id, data.user?.avatar)
                : `https://ui-avatars.com/api/?name=${data.user?.name}`}
              alt="user avatar"
              id="avatar-preview"
            />
          </div>
        </label>
        <input
          type="file"
          name="avatar"
          id="avatar"
          value=""
          accept="image/*"
          hidden
          onchange={showPreview}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Essential Fields -->
    <div class="divider divider-accent text-xl pt-8">Legal Details</div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Input
        id="legal_name"
        label="Legal Name"
        value={data?.user?.legal_name}
        required
        disabled={loading}
      />
      <Input
        id="email"
        type="email"
        label="Email"
        value={data?.user?.email}
        required
        disabled={loading}
      />
      <Input id="phone" type="tel" label="Phone" value={data?.user?.phone} disabled={loading} />
      <Input
        id="birthdate"
        type="date"
        label="Birth Date"
        value={data?.user?.birthdate}
        disabled={loading}
      />
    </div>

    <!-- Location Section -->
    <div class="divider divider-accent text-xl">Origin Location</div>
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input id="city" label="City" value={data?.user?.city} disabled={loading} />
        <div class="form-control w-full">
          <label for="country" class="label font-medium pb-1">
            <span class="label-text text-lg">Country</span>
          </label>
          <select
            id="country"
            name="country"
            class="select select-bordered w-full"
            disabled={loading}
          >
            <option value="">Select Country</option>
            {#each countries as country}
              <option value={country.code} selected={data.user?.country === country.code}>
                {country.name}
              </option>
            {/each}
          </select>
        </div>
      </div>
    </div>

    <!-- Biography Section -->
    <div class="divider divider-accent text-xl pt-8">Artist Biography</div>
    <div class="space-y-4">
      <Input
        id="website"
        type="url"
        label="Artist Website"
        value={data?.user?.website}
        disabled={loading}
      />
    </div>

    <!-- Music Platforms -->
    <div class="divider divider-accent text-xl pt-8">Music Platforms</div>
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          id="apple_music"
          type="url"
          label="Apple Music"
          value={data?.user?.apple_music}
          disabled={loading}
        />
        <Input
          id="spotify"
          type="url"
          label="Spotify"
          value={data?.user?.spotify}
          disabled={loading}
        />
        <Input
          id="soundcloud"
          type="url"
          label="SoundCloud"
          value={data?.user?.soundcloud}
          disabled={loading}
        />
        <Input
          id="bandcamp"
          type="url"
          label="Bandcamp"
          value={data?.user?.bandcamp}
          disabled={loading}
        />
        <Input
          id="youtube"
          type="url"
          label="YouTube"
          value={data?.user?.youtube}
          disabled={loading}
        />
        <Input
          id="mixcloud"
          type="url"
          label="Mixcloud"
          value={data?.user?.mixcloud}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Social Networks -->
    <div class="divider divider-accent text-xl pt-8">Social Networks</div>
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          id="instagram"
          type="url"
          label="Instagram"
          value={data?.user?.instagram}
          disabled={loading}
        />
        <Input
          id="facebook"
          type="url"
          label="Facebook"
          value={data?.user?.facebook}
          disabled={loading}
        />
        <Input id="x" type="url" label="X (Twitter)" value={data?.user?.x} disabled={loading} />
        <Input
          id="tiktok"
          type="url"
          label="TikTok"
          value={data?.user?.tiktok}
          disabled={loading}
        />

        <Input
          id="twitch"
          type="url"
          label="Twitch"
          value={data?.user?.twitch}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Event Platforms -->
    <div class="divider divider-accent text-xl pt-8">Event Platforms</div>
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          id="songkick"
          type="url"
          label="Songkick"
          value={data?.user?.songkick}
          disabled={loading}
        />
        <Input
          id="bandsintown"
          type="url"
          label="Bandsintown"
          value={data?.user?.bandsintown}
          disabled={loading}
        />
      </div>
    </div>

    <!-- Submit Button -->
    <div class="w-full max-w-lg pt-6">
      <button class="btn btn-accent" type="submit" disabled={loading}>
        {loading ? 'Updating Profile...' : 'Update Profile'}
      </button>
    </div>
  </form>
</SettingsContainer>
