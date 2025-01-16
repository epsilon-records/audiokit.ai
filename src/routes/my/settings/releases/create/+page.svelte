<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import SuperDebug from 'sveltekit-superforms';
  import { superForm } from 'sveltekit-superforms';
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';
  import { releaseSchema } from '$lib/schemas/release';

  let { data } = $props();

  const form = superForm(data.form, {
    resetForm: false,
    validators: zodClient(releaseSchema),
  });
  const { form: formData, enhance, message } = form;
</script>

<SettingsContainer title="Create Release">
  {#if $message}
    <h3>{$message}</h3>
  {/if}
  <svelte:fragment slot="description">Create a new release for your artist.</svelte:fragment>
  <div
    class="space-y-4 bg-yellow-100 rounded-lg border-2 border-yellow-200 px-8 pb-8 max-w-screen-lg"
  >
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

      <!-- Basic Release Information -->
      <div class="divider divider-accent text-2xl">Release Details</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="release_title">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Release Title</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.release_title}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">The main title of your release.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="release_version">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Version</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.release_version}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Optional version or edition information.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Release Metadata -->
      <div class="divider divider-accent text-2xl">Release Metadata</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="release_date">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Release Date</Label>
                <input
                  {...props}
                  type="date"
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.release_date}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">When will this release be available?</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="catalog_number">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Catalog Number</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.catalog_number}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Your internal catalog reference number.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="upc_code">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">UPC Code</Label>
                <input
                  {...props}
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.upc_code}
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Universal Product Code for distribution.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Description -->
      <div class="divider divider-accent text-2xl">Description</div>
      <div class="px-2">
        <div class="form-control w-full mb-2">
          <Field {form} name="description">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Release Description</Label>
                <textarea
                  {...props}
                  class="textarea textarea-bordered bg-white text-gray-900 h-32"
                  bind:value={$formData.description}
                ></textarea>
              {/snippet}
            </Control>
            <Description class="text-sm">Describe your release in detail.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Purchase Links -->
      <div class="divider divider-accent text-2xl">Purchase Links</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="bandcamp">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Bandcamp</Label>
                <input
                  {...props}
                  type="url"
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.bandcamp}
                  placeholder="https://artist.bandcamp.com/album/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Link to purchase digital release on Bandcamp.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
        <div class="form-control w-full max-w-lg mb-2">
          <Field {form} name="vinyl">
            <Control>
              {#snippet children({ props })}
                <Label class="text-xl">Vinyl Store</Label>
                <input
                  {...props}
                  type="url"
                  class="input input-bordered bg-white text-gray-900"
                  bind:value={$formData.vinyl}
                  placeholder="https://store.example.com/..."
                />
              {/snippet}
            </Control>
            <Description class="text-sm">Link to purchase vinyl version.</Description>
            <FieldErrors class="font-bold text-destructive mt-1" />
          </Field>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="w-full pt-8 px-2">
        <button class="btn btn-primary text-yellow-100" type="submit">Create Release</button>
      </div>

      <!-- Debug Data -->
      <SuperDebug data={$formData} />
    </form>
  </div>
</SettingsContainer>
