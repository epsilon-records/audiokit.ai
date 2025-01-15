<script lang="ts">
  import { Icon, Pencil } from 'svelte-hero-icons';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import SuperDebug from 'sveltekit-superforms';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { artistSchema } from '$lib/schemas/artist';

  let { data } = $props();

  const form = superForm(data.form, {
    resetForm: false,
    validators: zodClient(artistSchema),
    dataType: 'json',
  });
  const { form: formData, message, enhance } = form;
</script>

<SettingsContainer title="Edit Profile">
  {#if $message}
    <div class="mb-4">
      <span
        class={`badge ${
          $message.status == 200 ? 'badge-success' : 'badge-error'
        } px-4 py-3 text-lg font-medium`}
      >
        {$message}
      </span>
    </div>
  {/if}
  <svelte:fragment slot="description">Manage your artist profile.</svelte:fragment>
  <div class="space-y-4 bg-teal-100 rounded-lg border-2 border-teal-200 px-8 pb-8 max-w-screen-lg">
    <form
      method="POST"
      class="flex flex-col space-y-6 max-w-screen-lg"
      enctype="multipart/form-data"
      use:enhance
    >
      <!-- Hidden Fields -->
      <div>
        <Field {form} name="id">
          <Control>
            {#snippet children({ props })}
              <input {...props} type="hidden" bind:value={$formData.id} />
            {/snippet}
          </Control>
        </Field>
        <Field {form} name="org_id">
          <Control>
            {#snippet children({ props })}
              <input {...props} type="hidden" bind:value={$formData.org_id} />
            {/snippet}
          </Control>
        </Field>
      </div>

      <!-- Basic Information Section -->
      <div class="divider divider-accent text-2xl">Artist Profile</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="stage_name">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Artist Name</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.stage_name}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">This is your public artist name.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
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
      <div class="divider divider-accent text-2xl">Legal Details</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="legal_name">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Legal Name</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.legal_name}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Be sure to use your real name.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="phone">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Phone</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="tel"
                  bind:value={$formData.phone}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Used for urgent booking communications only.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="email">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Email</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="email"
                  bind:value={$formData.email}
                  required
                />
              {/snippet}
            </Control>
            <Description class="text-sm"
              >It's preferred that you use your company email.</Description
            >
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="birthdate">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Birthdate</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="date"
                  bind:value={$formData.birthdate}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Required for age-restricted venues and events.</Description
            >
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Location Section -->
      <div class="divider divider-accent text-2xl">Origin Location</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="city">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">City</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="text"
                  bind:value={$formData.city}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">The city you're primarily based in.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full">
          <label for="country" class="label font-medium pb-1">
            <span class="label-text text-lg">Country</span>
          </label>
          <select id="country" name="country" class="select select-bordered w-full">
            <option value="">Select Country</option>
          </select>
          <span class="text-sm text-muted-foreground mt-1">Your primary country of residence.</span>
        </div>
      </div>

      <!-- Biography Section -->
      <div class="divider divider-accent text-2xl">Artist Biography</div>
      <div class="space-y-4 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="website">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Artist Website</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.website}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official artist website or portfolio.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Music Platforms -->
      <div class="divider divider-accent text-2xl">Music Platforms</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="apple_music">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Apple Music</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.apple_music}
                  placeholder="https://music.apple.com/artist/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Apple Music artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="spotify">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Spotify</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.spotify}
                  placeholder="https://open.spotify.com/artist/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Spotify artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="soundcloud">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">SoundCloud</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.soundcloud}
                  placeholder="https://soundcloud.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official SoundCloud artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="bandcamp">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Bandcamp</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.bandcamp}
                  placeholder="https://artist.bandcamp.com"
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Bandcamp artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="youtube">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">YouTube</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.youtube}
                  placeholder="https://youtube.com/@..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official YouTube artist channel.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="mixcloud">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Mixcloud</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.mixcloud}
                  placeholder="https://mixcloud.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Mixcloud artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Social Networks -->
      <div class="divider divider-accent text-2xl">Social Networks</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="instagram">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Instagram</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.instagram}
                  placeholder="https://instagram.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Instagram profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="facebook">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Facebook</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.facebook}
                  placeholder="https://facebook.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Facebook artist page.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="x">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">X (Twitter)</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.x}
                  placeholder="https://x.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official X (Twitter) artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="tiktok">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">TikTok</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.tiktok}
                  placeholder="https://tiktok.com/@..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official TikTok artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="twitch">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Twitch</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.twitch}
                  placeholder="https://twitch.tv/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official Twitch artist channel.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="linkedin">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">LinkedIn</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.linkedin}
                  placeholder="https://linkedin.com/in/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your official LinkedIn artist profile.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Event Platforms -->
      <div class="divider divider-accent text-2xl">Event Platforms</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="songkick">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Songkick</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.songkick}
                  placeholder="https://songkick.com/artists/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your Songkick artist profile for tour dates.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="bandsintown">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Bandsintown</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  type="url"
                  bind:value={$formData.bandsintown}
                  placeholder="https://bandsintown.com/a/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm"
              >Your Bandsintown artist profile for tour dates.</Description
            >
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="w-full pt-8 px-2">
        <button class="btn btn-primary text-pink-100" type="submit"> Update Profile </button>
      </div>

      <!-- Debug Data -->
      <SuperDebug data={$formData} />
    </form>
  </div>
</SettingsContainer>
