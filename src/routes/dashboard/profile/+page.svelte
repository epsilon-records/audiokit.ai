<script lang="ts">
  import '$lib/styles/tiptap.css';
  import {
    Pencil,
    Bold,
    Italic,
    Strikethrough,
    List,
    ListOrdered,
    Quote as QuoteIcon,
    Save,
  } from 'lucide-svelte';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { artistSchema } from '$lib/schemas/artist';
  import SuperDebug from 'sveltekit-superforms';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { toast } from 'svelte-sonner';
  import confetti from 'canvas-confetti';
  import { Editor } from '@tiptap/core';
  import StarterKit from '@tiptap/starter-kit';
  import Placeholder from '@tiptap/extension-placeholder';
  import { onMount } from 'svelte';
  import { createUploadThing } from '$lib/utils/uploadthing';
  import type { OurFileRouter } from '$lib/server/uploadthing.js';

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
      }
      // Re-enable the button after the submission is complete
      isSubmitting = false;
    },
  });
  const { form: formData, enhance } = form;

  // Handle file upload preview
  let avatarPreview = $state('');

  // const uploadThing = createUploadThing<OurFileRouter>();

  async function handleAvatarChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    try {
      const [file] = input.files;
      // const res = await uploadThing['imageUploader'].upload([file]);

      if (false) {
        // avatarPreview = res[0].url;
        // $formData.artist_photos = [res[0].url];

        toast.success('Photo uploaded successfully');
      }
    } catch (err) {
      toast.error('Failed to upload photo');
    }
  }

  // Define editor state
  let editor = $state<Editor | null>(null);
  let editorContent = $state('');
  let editorElement: HTMLElement;

  // Initialize editor when element is available
  onMount(() => {
    if (!editorElement) return;

    editor = new Editor({
      element: editorElement,
      extensions: [
        StarterKit,
        Placeholder.configure({
          placeholder: 'Write your artist biography here...',
          emptyEditorClass: 'is-editor-empty',
        }),
      ],
      content: $formData.biography || '',
      editorProps: {
        attributes: {
          class: 'prose-sm sm:prose-base max-w-none min-h-[200px] p-4 focus:outline-none',
        },
      },
      onUpdate: ({ editor }) => {
        const content = editor.getHTML();
        editorContent = content;
        $formData.biography = content;
      },
    });

    // Cleanup on unmount
    return () => {
      editor?.destroy();
    };
  });

  // Editor control functions
  function toggleFormat(
    type: 'bold' | 'italic' | 'strike' | 'bulletList' | 'orderedList' | 'blockquote'
  ) {
    if (!editor) return;

    const commands = {
      bold: () => editor?.chain().focus().toggleBold().run(),
      italic: () => editor?.chain().focus().toggleItalic().run(),
      strike: () => editor?.chain().focus().toggleStrike().run(),
      bulletList: () => editor?.chain().focus().toggleBulletList().run(),
      orderedList: () => editor?.chain().focus().toggleOrderedList().run(),
      blockquote: () => editor?.chain().focus().toggleBlockquote().run(),
    };

    commands[type]();
  }

  // Add editor control functions
  function toggleBold() {
    editor?.chain().focus().toggleBold().run();
  }

  function toggleItalic() {
    editor?.chain().focus().toggleItalic().run();
  }

  function toggleStrike() {
    editor?.chain().focus().toggleStrike().run();
  }

  function toggleBulletList() {
    editor?.chain().focus().toggleBulletList().run();
  }

  function toggleOrderedList() {
    editor?.chain().focus().toggleOrderedList().run();
  }

  function toggleBlockquote() {
    editor?.chain().focus().toggleBlockquote().run();
  }
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Profile</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Manage your artist information, biography, and social media presence.
    </p>
    <div class="mt-4">
      <span
        class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20"
      >
        <span class="mr-1.5 h-1.5 w-1.5 rounded-full bg-green-600" />
        Profile is public and visible to fans
      </span>
    </div>
  </div>

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
          <div class="form-control w-full max-w-lg mb-2">
            <Field {form} name="avatar">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Artist Photo</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <label for="avatar" class="avatar w-32 rounded-full hover:cursor-pointer">
                    <label
                      for="avatar"
                      class="absolute -bottom-0.5 -right-0.5 hover:cursor-pointer"
                    >
                      <span class="btn btn-circle btn-sm btn-secondary">
                        <Pencil class="w-4 h-4" />
                      </span>
                    </label>
                    <div class="w-32">
                      <!-- <img
                        src={avatarPreview || $formData.artist_photos?.[0] || '/logo.gif'}
                        alt="Artist photo"
                        class="rounded-full object-cover w-full h-full"
                      /> -->
                    </div>
                  </label>
                  <input
                    {...props}
                    type="file"
                    name="avatar"
                    id="avatar"
                    accept="image/*"
                    hidden
                    onchange={handleAvatarChange}
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Upload a professional photo (max 4MB)</Description>
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
      <CardHeader class="bg-gradient-to-r from-green-50 to-green-100 pb-4">
        <CardTitle>📍 Current Location</CardTitle>
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
                  >
                    <option value="">Select Country</option>
                    <!-- Add your country options here -->
                  </select>
                {/snippet}
              </Control>
              <Description class="text-sm">Your primary country of residence.</Description>
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
                  />
                {/snippet}
              </Control>
              <Description class="text-sm">Your official artist website or portfolio.</Description>
            </Field>
          </div>

          <div class="form-control w-full mb-2">
            <Field {form} name="biography">
              <Control>
                {#snippet children({ props })}
                  <div class="flex justify-between items-center">
                    <Label class="text-base font-bold">Biography</Label>
                    <FieldErrors class="font-bold text-destructive text-sm" />
                  </div>
                  <div class="border rounded-md bg-white text-gray-900 overflow-hidden">
                    <!-- Toolbar -->
                    <div class="border-b p-2 flex gap-2 bg-gray-50">
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'bold'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('bold')}
                      >
                        <Bold class="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'italic'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('italic')}
                      >
                        <Italic class="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'strike'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('strike')}
                      >
                        <Strikethrough class="w-4 h-4" />
                      </button>
                      <div class="w-px h-6 bg-gray-300 mx-1" />
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'bulletList'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('bulletList')}
                      >
                        <List class="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'orderedList'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('orderedList')}
                      >
                        <ListOrdered class="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        class="p-2 rounded-md transition-colors hover:bg-gray-200 {editor?.isActive(
                          'blockquote'
                        )
                          ? 'bg-gray-200'
                          : ''}"
                        onclick={() => toggleFormat('blockquote')}
                      >
                        <QuoteIcon class="w-4 h-4" />
                      </button>
                    </div>

                    <!-- Editor Content -->
                    <div bind:this={editorElement} class="tiptap-editor" />
                    <input type="hidden" name="biography" value={editorContent} />
                  </div>
                  <input type="hidden" {...props} value={editorContent} />
                {/snippet}
              </Control>
              <Description class="text-sm">Share your story and musical journey.</Description>
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

    <!-- Submit button card with transparent background -->
    <Card class="bg-transparent border-none shadow-none">
      <CardContent class="flex justify-end p-0">
        <button
          class="btn btn-accent hover:bg-accent hover:text-accent-foreground transition-colors"
          type="submit"
          disabled={isSubmitting}
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

    <!-- Debug card remains the same -->
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

<style>
  :global(.tiptap-editor) {
    @apply prose-sm sm:prose-base max-w-none min-h-[200px] p-4;
  }

  :global(.tiptap-editor p.is-editor-empty:first-child::before) {
    @apply text-muted-foreground;
    content: attr(data-placeholder);
    float: left;
    height: 0;
    pointer-events: none;
  }

  :global(.tiptap-editor:focus) {
    @apply outline-none;
  }
</style>
