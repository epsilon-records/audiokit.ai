<script lang="ts">
  import '$lib/styles/tiptap.css';
  import { Save } from 'lucide-svelte';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { artistSchema } from '$lib/schemas/artist';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { toast } from 'svelte-sonner';
  import confetti from 'canvas-confetti';
  // import SuperDebug from 'sveltekit-superforms';

  let { data } = $props();

  let isSubmitting = $state(false);

  const form = superForm(data.form, {
    resetForm: false,
    validators: zodClient(artistSchema),
    dataType: 'json',
    onSubmit: () => {
      isSubmitting = true;
    },
    onResult: ({ result }) => {
      if (result.type === 'success') {
        toast.success('Artist profile updated', {
          description: 'Your changes are now live',
        });

        // Create fireworks effect
        const duration = 5 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min: number, max: number) {
          return Math.random() * (max - min) + min;
        }

        const interval: any = setInterval(function () {
          const timeLeft = animationEnd - Date.now();

          if (timeLeft <= 0) {
            return clearInterval(interval);
          }

          const particleCount = 50 * (timeLeft / duration);

          // Since particles fall down, start a bit higher than random
          confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
          });
          confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
          });
        }, 250);
      } else {
        toast.error('Error updating profile', {
          description: 'Please check the form for errors and try again',
        });
      }

      // Re-enable the button after the submission is complete
      isSubmitting = false;
    },
  });
  const { form: formData, enhance } = form;
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Profile</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Manage your artist information, biography, and social media presence.
    </p>
  </div>

  <div class:opacity-50={isSubmitting} class:pointer-events-none={isSubmitting}>
    <form method="POST" class="space-y-6" enctype="multipart/form-data" use:enhance>
      <!-- Basic Information Card -->
      <Card>
        <CardHeader class="bg-gradient-to-r from-blue-50 to-blue-100 pb-4">
          <CardTitle>👤 Artist Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <Field {form} name="id">
              <Control>
                {#snippet children({ props })}
                  <input {...props} type="hidden" bind:value={$formData.id} />
                {/snippet}
              </Control>
            </Field>
            <Field {form} name="orgId">
              <Control>
                {#snippet children({ props })}
                  <input {...props} type="hidden" bind:value={$formData.orgId} />
                {/snippet}
              </Control>
            </Field>
            <Field {form} name="isSigned">
              <Control>
                {#snippet children({ props })}
                  <input {...props} type="hidden" bind:value={$formData.isSigned} />
                {/snippet}
              </Control>
            </Field>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-control w-full max-w-lg mb-2">
              <Field {form} name="stageName">
                <Control>
                  {#snippet children({ props })}
                    <div class="flex justify-between items-center">
                      <Label class="text-base font-bold">Artist Name</Label>
                      <FieldErrors class="font-bold text-destructive text-sm" />
                    </div>
                    <input
                      {...props}
                      class="input input-bordered bg-white text-gray-900"
                      bind:value={$formData.stageName}
                      disabled={!!data.form?.data?.stageName}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.stageName}
                    Artist stage name cannot be changed.
                  {:else}
                    Enter your exact public artist/stage name with desired spelling and
                    capitalization. This will be displayed on your profile and releases.
                  {/if}
                </Description>
              </Field>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Legal Details Card -->
      <Card>
        <CardHeader class="bg-gradient-to-r from-purple-50 to-purple-100 pb-4">
          <CardTitle>📋 Legal Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-control w-full max-w-lg mb-2">
              <Field {form} name="legalName">
                <Control>
                  {#snippet children({ props })}
                    <div class="flex justify-between items-center">
                      <Label class="text-base font-bold">Legal Name</Label>
                      <FieldErrors class="font-bold text-destructive text-sm" />
                    </div>
                    <input
                      {...props}
                      class="input input-bordered bg-white text-gray-900"
                      bind:value={$formData.legalName}
                      disabled={!!data.form?.data?.legalName}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.legalName}
                    Legal name can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Be sure to use your full legal name.
                  {/if}
                </Description>
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
                <Description class="text-sm">
                  Used for urgent booking communications only.
                </Description>
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
                      disabled={!!data.form?.data?.email}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.email}
                    Email can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    It's preferred that you use your company email.
                  {/if}
                </Description>
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
                      disabled={!!data.form?.data?.birthdate}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  Required for age-restricted venues and events.
                </Description>
              </Field>
            </div>
            <div class="form-control w-full max-w-lg mb-2">
              <Field {form} name="address">
                <Control>
                  {#snippet children({ props })}
                    <div class="flex justify-between items-center">
                      <Label class="text-base font-bold">Address</Label>
                      <FieldErrors class="font-bold text-destructive text-sm" />
                    </div>
                    <input
                      {...props}
                      class="input input-bordered bg-white text-gray-900"
                      type="text"
                      bind:value={$formData.address}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  Your legal address for contracts and payments.
                </Description>
              </Field>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Location Card -->
      <Card>
        <CardHeader class="bg-gradient-to-r from-green-50 to-green-100 pb-4">
          <CardTitle>📍 Origin Location</CardTitle>
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
                      disabled={!!data.form?.data?.city}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.city}
                    City of origin can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    The city you're originally from or started your career in.
                  {/if}
                </Description>
              </Field>
            </div>
            <div class="form-control w-full max-w-lg mb-2">
              <Field {form} name="country">
                <Control>
                  {#snippet children({ props })}
                    <div class="flex justify-between items-center">
                      <Label class="text-base font-bold">Country</Label>
                      <FieldErrors class="font-bold text-destructive text-sm" />
                    </div>
                    <select
                      {...props}
                      class="select select-bordered w-full bg-white text-gray-900"
                      bind:value={$formData.country}
                      disabled={!!data.form?.data?.country}
                    >
                      <option value="">Select Country</option>
                      <!-- Add your country options here -->
                    </select>
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.country}
                    Country of origin can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Your country of origin or where you started your career.
                  {/if}
                </Description>
              </Field>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Biography Card -->
      <Card>
        <CardHeader class="bg-gradient-to-r from-yellow-50 to-yellow-100 pb-4">
          <CardTitle>📝 Artist Biography</CardTitle>
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
                      disabled={!!data.form?.data?.website}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  Your official artist website or portfolio.
                </Description>
              </Field>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Music Platforms Card -->
      <Card>
        <CardHeader class="bg-gradient-to-r from-red-50 to-red-100 pb-4">
          <CardTitle>🎵 Music Platforms</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-control w-full max-w-lg mb-2">
              <Field {form} name="appleMusic">
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
                      bind:value={$formData.appleMusic}
                      placeholder="https://music.apple.com/artist/..."
                      disabled={!!data.form?.data?.appleMusic}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.appleMusic}
                    Platform links can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Your official Apple Music artist profile.
                  {/if}
                </Description>
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
                      disabled={!!data.form?.data?.spotify}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.spotify}
                    Platform links can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Your official Spotify artist profile.
                  {/if}
                </Description>
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
                      disabled={!!data.form?.data?.soundcloud}
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
                      disabled={!!data.form?.data?.bandcamp}
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
                      disabled={!!data.form?.data?.youtube}
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
                      disabled={!!data.form?.data?.mixcloud}
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
        <CardHeader class="bg-gradient-to-r from-indigo-50 to-indigo-100 pb-4">
          <CardTitle>🌐 Social Networks</CardTitle>
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
                      disabled={!!data.form?.data?.instagram}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.instagram}
                    Platform links can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Your official Instagram profile.
                  {/if}
                </Description>
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
                      disabled={!!data.form?.data?.facebook}
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
                      disabled={!!data.form?.data?.x}
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
                      disabled={!!data.form?.data?.tiktok}
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
                      disabled={!!data.form?.data?.twitch}
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
                      disabled={!!data.form?.data?.linkedin}
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
        <CardHeader class="bg-gradient-to-r from-pink-50 to-pink-100 pb-4">
          <CardTitle>🎫 Event Platforms</CardTitle>
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
                      disabled={!!data.form?.data?.songkick}
                    />
                  {/snippet}
                </Control>
                <Description class="text-sm">
                  {#if !!data.form?.data?.songkick}
                    Platform links can be changed by contacting <a
                      href="/support"
                      class="text-green-700 hover:underline">support</a
                    >.
                  {:else}
                    Your Songkick artist profile for tour dates.
                  {/if}
                </Description>
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
                      disabled={!!data.form?.data?.bandsintown}
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

      <!-- Submit button card with transparent background -->
      <Card class="bg-transparent border-none shadow-none">
        <CardContent class="flex justify-end p-0">
          <button
            class="btn btn-accent hover:bg-accent hover:text-accent-foreground transition-colors"
            type="submit"
          >
            {#if isSubmitting}
              <span class="loading loading-spinner loading-sm"></span>
            {:else}
              <Save class="w-4 h-4" />
            {/if}
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </button>
        </CardContent>
      </Card>

      <!-- Debug -->
      <!-- <Card>
        <CardHeader class="bg-gradient-to-r from-gray-50 to-gray-100 pb-4">
          <CardTitle>Debug Data</CardTitle>
        </CardHeader>
        <CardContent>
          <SuperDebug data={$formData} />
        </CardContent>
      </Card> -->
    </form>
  </div>
</div>
