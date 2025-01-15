<script lang="ts">
  import { Icon, Pencil } from 'svelte-hero-icons';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import SuperDebug from 'sveltekit-superforms';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { artistSchema } from '$lib/schemas/artist';

  let { data } = $props<{ form: any }>();
  const form = superForm(data.form, {
    resetForm: false,
    validators: zodClient(artistSchema),
  });
  const { form: formData, enhance, message } = form;
</script>

<SettingsContainer title="Edit Profile">
  {#if $message}
    <h3>{$message}</h3>
  {/if}
  <svelte:fragment slot="description">Manage your artist profile.</svelte:fragment>
  <div class="space-y-4 bg-white rounded-lg border border-gray-200 p-6">
    <h3 class="text-2xl font-semibold">Select Artist</h3>
    <div class="rounded-lg">
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/my/settings/profile"
        afterSelectOrganizationUrl="/my/settings/profile"
      />
    </div>
    <p class="text-muted-foreground">
      Choose the artist profile you want to edit. You can switch between different artists or create
      a new artist profile.
    </p>
  </div>
  <div class="space-y-4 bg-white rounded-lg border border-gray-200 p-6">
    <form
      method="POST"
      class="flex flex-col space-y-6 w-full"
      enctype="multipart/form-data"
      use:enhance
    >
      Basic Information Section
      <div class="divider divider-accent text-2xl">Artist Profile</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="stage_name">
          <Control>
            {#snippet children({ props })}
              <Label>Artist Name</Label>
              <input {...props} bind:value={$formData.stage_name} />
            {/snippet}
          </Control>
          <Description>This is your public artist name.</Description>
          <FieldErrors />
        </Field>
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
              <!-- <img
                src={data.user?.avatar
                  ? getImageURL(data.user?.collectionId, data.user?.id, data.user?.avatar)
                  : `https://ui-avatars.com/api/?name=${data.user?.name}`}
                alt="user avatar"
                id="avatar-preview"
              /> -->
            </div>
          </label>
          <input type="file" name="avatar" id="avatar" value="" accept="image/*" hidden />
        </div>
      </div>

      <!-- Essential Fields -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Legal Details</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="legal_name">
          <Control>
            {#snippet children({ props })}
              <Label>Legal Name</Label>
              <input {...props} bind:value={$formData.legal_name} />
            {/snippet}
          </Control>
          <Description>Be sure to use your real name.</Description>
          <FieldErrors />
        </Field>
        <Field {form} name="phone">
          <Control>
            {#snippet children({ props })}
              <Label>Phone</Label>
              <input {...props} type="tel" bind:value={$formData.phone} />
            {/snippet}
          </Control>
          <Description>Used for urgent booking communications only.</Description>
          <FieldErrors />
        </Field>
        <Field {form} name="email">
          <Control>
            {#snippet children({ props })}
              <Label>Email</Label>
              <input {...props} type="email" bind:value={$formData.email} required />
            {/snippet}
          </Control>
          <Description>It's preferred that you use your company email.</Description>
          <FieldErrors />
        </Field>
        <Field {form} name="birthdate">
          <Control>
            {#snippet children({ props })}
              <Label>Birth Date</Label>
              <input {...props} type="date" bind:value={$formData.birthdate} />
            {/snippet}
          </Control>
          <Description>Required for age-restricted venues and events.</Description>
          <FieldErrors />
        </Field>
      </div>

      <!-- Location Section -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Origin Location</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="city">
          <Control>
            {#snippet children({ props })}
              <Label>City</Label>
              <input {...props} type="text" bind:value={$formData.city} />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <div class="form-control w-full">
          <label for="country" class="label font-medium pb-1">
            <span class="label-text text-lg">Country</span>
          </label>
          <select id="country" name="country" class="select select-bordered w-full">
            <option value="">Select Country</option>
            <!-- {#each countries as country}
              <option value={country.code} selected={data.user?.country === country.code}>
                {country.name}
              </option>
            {/each} -->
          </select>
        </div>
      </div>

      <!-- Biography Section -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Artist Biography</div>
      <div class="space-y-4 px-2">
        <Field {form} name="website">
          <Control>
            {#snippet children({ props })}
              <Label>Artist Website</Label>
              <input {...props} type="url" bind:value={$formData.website} />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
      </div>

      <!-- Music Platforms -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Music Platforms</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="apple_music">
          <Control>
            {#snippet children({ props })}
              <Label>Apple Music</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.apple_music}
                placeholder="https://music.apple.com/artist/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="spotify">
          <Control>
            {#snippet children({ props })}
              <Label>Spotify</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.spotify}
                placeholder="https://open.spotify.com/artist/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="soundcloud">
          <Control>
            {#snippet children({ props })}
              <Label>SoundCloud</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.soundcloud}
                placeholder="https://soundcloud.com/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="bandcamp">
          <Control>
            {#snippet children({ props })}
              <Label>Bandcamp</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.bandcamp}
                placeholder="https://artist.bandcamp.com"
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="youtube">
          <Control>
            {#snippet children({ props })}
              <Label>YouTube</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.youtube}
                placeholder="https://youtube.com/@..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="mixcloud">
          <Control>
            {#snippet children({ props })}
              <Label>Mixcloud</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.mixcloud}
                placeholder="https://mixcloud.com/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
      </div>

      <!-- Social Networks -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Social Networks</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="instagram">
          <Control>
            {#snippet children({ props })}
              <Label>Instagram</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.instagram}
                placeholder="https://instagram.com/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="facebook">
          <Control>
            {#snippet children({ props })}
              <Label>Facebook</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.facebook}
                placeholder="https://facebook.com/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="x">
          <Control>
            {#snippet children({ props })}
              <Label>X (Twitter)</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.x}
                placeholder="https://x.com/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="tiktok">
          <Control>
            {#snippet children({ props })}
              <Label>TikTok</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.tiktok}
                placeholder="https://tiktok.com/@..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="twitch">
          <Control>
            {#snippet children({ props })}
              <Label>Twitch</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.twitch}
                placeholder="https://twitch.tv/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
      </div>

      <!-- Event Platforms -->
      <div class="divider divider-accent text-2xl pt-16 mt-8">Event Platforms</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <Field {form} name="songkick">
          <Control>
            {#snippet children({ props })}
              <Label>Songkick</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.songkick}
                placeholder="https://songkick.com/artists/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
        <Field {form} name="bandsintown">
          <Control>
            {#snippet children({ props })}
              <Label>Bandsintown</Label>
              <input
                {...props}
                type="url"
                bind:value={$formData.bandsintown}
                placeholder="https://bandsintown.com/a/..."
              />
            {/snippet}
          </Control>
          <FieldErrors />
        </Field>
      </div>

      <!-- Submit Button -->
      <div class="w-full pt-8 px-2">
        <button class="btn btn-primary text-pink-100" type="submit"> Update Profile </button>
      </div>
    </form>

    <!-- Debug Data -->
    <SuperDebug data={$form} />
  </div>
</SettingsContainer>
