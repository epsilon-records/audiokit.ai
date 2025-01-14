<script lang="ts">
  import { superForm } from 'sveltekit-superforms/client';
  import SuperDebug from 'sveltekit-superforms';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import type { PageData } from './$types';

  let { data } = $props();

  const { form, errors, enhance } = superForm(data.form);
</script>

<div class="container mx-auto px-4 py-8">
  <Card class="max-w-3xl mx-auto bg-card">
    <CardHeader>
      <CardTitle>Edit Artist Profile</CardTitle>
    </CardHeader>
    <CardContent>
      <form method="POST" use:enhance class="space-y-8">
        <!-- Hidden Fields -->
        <input type="hidden" name="id" bind:value={$form.id} />
        <input type="hidden" name="legal_name" bind:value={$form.legal_name} />
        <input type="hidden" name="email" bind:value={$form.email} />
        <input type="hidden" name="slug" bind:value={$form.slug} />
        <input type="hidden" name="phone" bind:value={$form.phone} />
        <input type="hidden" name="birthdate" bind:value={$form.birthdate} />
        <input type="hidden" name="city" bind:value={$form.city} />
        <input type="hidden" name="country" bind:value={$form.country} />
        <input type="hidden" name="artist_photos" bind:value={$form.artist_photos} />
        <input type="hidden" name="anr" bind:value={$form.anr} />

        <!-- Visible form content starts here -->
        <div class="space-y-6">
          <h3 class="text-lg font-semibold">Essential Information</h3>
          <div class="grid grid-cols-1 gap-6">
            <div class="space-y-2">
              <Label for="stage_name">Stage Name *</Label>
              <Input
                id="stage_name"
                name="stage_name"
                bind:value={$form.stage_name}
                class="bg-background"
                aria-invalid={$errors.stage_name ? 'true' : undefined}
                required
              />
              {#if $errors.stage_name}<span class="text-destructive text-sm"
                  >{$errors.stage_name}</span
                >{/if}
            </div>
          </div>
        </div>

        <!-- Professional Information -->
        <div class="space-y-6">
          <h3 class="text-lg font-semibold">Professional Information</h3>
          <div class="space-y-2">
            <Label for="biography">Biography</Label>
            <Textarea
              id="biography"
              bind:value={$form.biography}
              class="bg-background min-h-[200px]"
              aria-invalid={$errors.biography ? 'true' : undefined}
            />
            {#if $errors.biography}<span class="text-destructive text-sm">{$errors.biography}</span
              >{/if}
          </div>
        </div>

        <!-- Social Media Links -->
        <div class="space-y-6">
          <h3 class="text-lg font-semibold">Music Platforms</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <Label for="spotify">Spotify</Label>
              <Input
                id="spotify"
                name="spotify"
                bind:value={$form.spotify}
                class="bg-background"
                placeholder="Spotify Artist URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="apple_music">Apple Music</Label>
              <Input
                id="apple_music"
                name="apple_music"
                bind:value={$form.apple_music}
                class="bg-background"
                placeholder="Apple Music URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="soundcloud">SoundCloud</Label>
              <Input
                id="soundcloud"
                name="soundcloud"
                bind:value={$form.soundcloud}
                class="bg-background"
                placeholder="SoundCloud URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="bandcamp">Bandcamp</Label>
              <Input
                id="bandcamp"
                name="bandcamp"
                bind:value={$form.bandcamp}
                class="bg-background"
                placeholder="Bandcamp URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="mixcloud">Mixcloud</Label>
              <Input
                id="mixcloud"
                name="mixcloud"
                bind:value={$form.mixcloud}
                class="bg-background"
                placeholder="Mixcloud URL"
              />
            </div>
          </div>
        </div>

        <!-- Social Media Links -->
        <div class="space-y-6">
          <h3 class="text-lg font-semibold">Social Media</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <Label for="website">Website</Label>
              <Input
                id="website"
                name="website"
                bind:value={$form.website}
                class="bg-background"
                placeholder="Personal Website URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="instagram">Instagram</Label>
              <Input
                id="instagram"
                name="instagram"
                bind:value={$form.instagram}
                class="bg-background"
                placeholder="Instagram URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="facebook">Facebook</Label>
              <Input
                id="facebook"
                name="facebook"
                bind:value={$form.facebook}
                class="bg-background"
                placeholder="Facebook URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="x">X (Twitter)</Label>
              <Input
                id="x"
                name="x"
                bind:value={$form.x}
                class="bg-background"
                placeholder="X Profile URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="tiktok">TikTok</Label>
              <Input
                id="tiktok"
                name="tiktok"
                bind:value={$form.tiktok}
                class="bg-background"
                placeholder="TikTok Profile URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="youtube">YouTube</Label>
              <Input
                id="youtube"
                name="youtube"
                bind:value={$form.youtube}
                class="bg-background"
                placeholder="YouTube Channel URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="twitch">Twitch</Label>
              <Input
                id="twitch"
                name="twitch"
                bind:value={$form.twitch}
                class="bg-background"
                placeholder="Twitch Channel URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="snapchat">Snapchat</Label>
              <Input
                id="snapchat"
                name="snapchat"
                bind:value={$form.snapchat}
                class="bg-background"
                placeholder="Snapchat URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="linkedin">LinkedIn</Label>
              <Input
                id="linkedin"
                name="linkedin"
                bind:value={$form.linkedin}
                class="bg-background"
                placeholder="LinkedIn URL"
              />
            </div>
          </div>
        </div>

        <!-- Event Platforms -->
        <div class="space-y-6">
          <h3 class="text-lg font-semibold">Event Platforms</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <Label for="songkick">Songkick</Label>
              <Input
                id="songkick"
                name="songkick"
                bind:value={$form.songkick}
                class="bg-background"
                placeholder="Songkick URL"
              />
            </div>

            <div class="space-y-2">
              <Label for="bandsintown">Bandsintown</Label>
              <Input
                id="bandsintown"
                name="bandsintown"
                bind:value={$form.bandsintown}
                class="bg-background"
                placeholder="Bandsintown URL"
              />
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-4 pt-6">
          <Button variant="outline" href="/artists">Cancel</Button>
          <Button type="submit">Save Changes</Button>
        </div>
      </form>
    </CardContent>
  </Card>
  <SuperDebug data={$form} />
</div>
