<script lang="ts">
  import { Field, Control, Label, Description, FieldErrors } from 'formsnap';

  let { form } = $props();
</script>

<section class="mb-12">
  <h2
    class="text-2xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Location
  </h2>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="form-control w-full">
        <Field {form} name="city">
          <Control>
            {#snippet children({ props })}
              <Label class="text-base font-medium text-gray-900 dark:text-gray-100">City</Label>
              <input
                {...props}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                bind:value={form.data.city}
              />
            {/snippet}
          </Control>
          <Description>Your current city</Description>
          <FieldErrors />
        </Field>
      </div>

      <div class="form-control w-full">
        <Field {form} name="country">
          <Control>
            {#snippet children({ props })}
              <Label class="text-base font-medium text-gray-900 dark:text-gray-100">Country</Label>
              <select
                {...props}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                bind:value={form.data.country}
              >
                <option value="">Select a country</option>
                <!-- Add country options here -->
              </select>
            {/snippet}
          </Control>
          <Description>Your current country</Description>
          <FieldErrors />
        </Field>
      </div>
    </div>
  </div>
</section>
