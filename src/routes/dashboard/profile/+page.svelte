<script lang="ts">
  import { Icon, Pencil } from 'svelte-hero-icons';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { artistSchema } from '$lib/schemas/artist';
  import { fade } from 'svelte/transition';
  import SuperDebug from 'sveltekit-superforms';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';

  let { data } = $props();

  const form = superForm(data.form, {
    resetForm: false,
    validators: zodClient(artistSchema),
    dataType: 'json',
  });
  const { form: formData, message, enhance } = form;

  // Handle file upload preview
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

<div class="container mx-auto px-4 py-8">
  {#if !data.hasActiveSubscription}
    <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-8 rounded" in:fade>
      <p class="text-yellow-700">
        <span class="font-bold">Limited Access:</span>
        Upgrade to Pro to unlock all profile features.
      </p>
    </div>
  {/if}

  <form method="POST" class="space-y-6" enctype="multipart/form-data" use:enhance>
    <!-- Hidden Fields Card -->
    <Card>
      <CardContent class="pt-6">
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
          <Field {form} name="is_signed">
            <Control>
              {#snippet children({ props })}
                <input {...props} type="hidden" bind:value={$formData.is_signed} />
              {/snippet}
            </Control>
          </Field>
        </div>
      </CardContent>
    </Card>

    <!-- Basic Information Card -->
    <Card>
      <CardHeader>
        <CardTitle>Artist Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="stage_name">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Artist Name</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    bind:value={$formData.stage_name}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">This is your public artist stage name.</Description>
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
      </CardContent>
    </Card>

    <!-- Legal Details Card -->
    <Card>
      <CardHeader>
        <CardTitle>Legal Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="legal_name">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Legal Name</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    bind:value={$formData.legal_name}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Be sure to use your real name.</Description>
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="phone">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Phone</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    type="tel"
                    bind:value={$formData.phone}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Used for urgent booking communications only.</Description
              >
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="email">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Email</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="birthdate">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Birthdate</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    type="date"
                    bind:value={$formData.birthdate}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm"
                >Required for age-restricted venues and events.</Description
              >
            </Field>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Location Card -->
    <Card>
      <CardHeader>
        <CardTitle>Current Location</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="city">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">City</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    type="text"
                    bind:value={$formData.city}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">The city you're primarily based in.</Description>
            </Field>
          </div>
          <div class="form-control w-full">
            <label for="country" class="label font-medium pb-1">
              <span class="label-text text-lg">Country</span>
            </label>
            <select id="country" name="country" class="select select-bordered w-full">
              <option value="">Select Country</option>
            </select>
            <span class="text-sm text-muted-foreground mt-1"
              >Your primary country of residence.</span
            >
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Biography Card -->
    <Card>
      <CardHeader>
        <CardTitle>Artist Biography</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="space-y-4">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="website">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Artist Website</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    type="url"
                    bind:value={$formData.website}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Your official artist website or portfolio.</Description>
            </Field>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Music Platforms Card -->
    <Card>
      <CardHeader>
        <CardTitle>Music Platforms</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="apple_music">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Apple Music</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="spotify">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Spotify</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="soundcloud">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">SoundCloud</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="bandcamp">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Bandcamp</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="youtube">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">YouTube</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="mixcloud">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Mixcloud</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Social Networks Card -->
    <Card>
      <CardHeader>
        <CardTitle>Social Networks</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="instagram">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Instagram</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="facebook">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Facebook</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="x">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">X (Twitter)</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="tiktok">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">TikTok</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="twitch">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Twitch</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="linkedin">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">LinkedIn</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Event Platforms Card -->
    <Card>
      <CardHeader>
        <CardTitle>Event Platforms</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="songkick">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Songkick</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <input
                    {...props}
                    class="input input-bordered bg-white text-gray-900"
                    type="url"
                    bind:value={$formData.songkick}
                    placeholder="https://songkick.com/artists/..."
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Your Songkick artist profile for tour dates.</Description
              >
            </Field>
          </div>
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="bandsintown">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Bandsintown</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
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
            </Field>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Submit Button -->
    <div class="flex justify-end">
      <button class="btn btn-primary text-pink-100" type="submit">Update Profile</button>
    </div>

    <!-- Debug Data -->
    <SuperDebug data={$formData} />
  </form>
</div>
