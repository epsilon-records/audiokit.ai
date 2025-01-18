<script lang="ts">
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';

  let { form } = $props();
</script>

<section class="mb-12">
  <h2
    class="text-2xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Biography
  </h2>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <div class="space-y-6">
      <div class="form-control w-full">
        <Field {form} name="biography">
          <Control>
            {#snippet children({ props })}
              <Label class="text-base font-medium text-gray-900 dark:text-gray-100"
                >Artist Bio</Label
              >
              <textarea
                {...props}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                rows="6"
                bind:value={form.data.biography}
              ></textarea>
            {/snippet}
          </Control>
          <Description>Tell your story and share your journey as an artist</Description>
          <FieldErrors />
        </Field>
      </div>
    </div>
  </div>
</section>
