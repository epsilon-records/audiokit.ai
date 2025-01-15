<script lang="ts">
  import { enhance, applyAction } from '$app/forms';
  import { invalidateAll } from '$app/navigation';
  import { Icon, Pencil } from 'svelte-hero-icons';
  import Input from '$lib/components/Input.svelte';
  import { getImageURL } from '$lib/utils';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';

  let { data } = $props<{ data: { user: any } }>();
  let loading = $state(false);

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
    return async ({ result }: { result: any }) => {
      switch (result.type) {
        case 'success':
          await invalidateAll();
          break;
        case 'error':
          break;
        default:
          await applyAction(result);
      }
      loading = false;
    };
  };
</script>

<SettingsContainer title="Profile">
  <svelte:fragment slot="description">Manage your profile information and avatar.</svelte:fragment>

  <form
    action="?/updateProfile"
    method="POST"
    class="flex flex-col space-y-2 w-full"
    enctype="multipart/form-data"
    use:enhance={submitUpdateProfile}
  >
    <div class="form-control w-full max-w-lg">
      <label for="avatar" class="label font-medium pb-1">
        <span class="label-text text-xl">Profile Picture</span>
      </label>
      <label for="avatar" class="avatar w-32 rounded-full hover:cursor-pointer">
        <label for="avatar" class="absolute -bottom-0.5 -right-0.5 hover:cursor-pointer">
          <span class="btn btn-circle btn-sm btn-secondary">
            <Icon src={Pencil} class="w-4 h-4" />
          </span>
        </label>
        <div class="w-32 rounded-full">
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
    <Input id="name" label="Name" value={data?.user?.name} disabled={loading} />
    <div class="w-full max-w-lg pt-3">
      <button class="btn btn-primary w-full max-w-lg" type="submit" disabled={loading}>
        Update Profile
      </button>
    </div>
  </form>
</SettingsContainer>
