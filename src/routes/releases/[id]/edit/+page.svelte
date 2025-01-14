<script lang="ts">
  import { superForm } from 'sveltekit-superforms/client';
  import { Button } from '$lib/components/ui/button';
  import Form from '$lib/components/Form.svelte';
  import FormField from '$lib/components/FormField.svelte';
  import FormTextarea from '$lib/components/FormTextarea.svelte';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import { validators } from '$lib/utils/validation';
  import type { PageData } from './$types';

  let { data } = $props<{ data: PageData }>();
  const { form, errors, enhance } = superForm(data.form);

  const validation = {
    title: [validators.required()],
    catalog_number: [validators.required()],
    description: [validators.required(), validators.minLength(10)],
    release_date: [validators.required()],
    price: [validators.required()],
  };
</script>

<PageContainer>
  <Form {validation} class="max-w-3xl mx-auto">
    <FormField
      label="Title"
      id="title"
      bind:value={$form.title}
      error={$errors.title}
      rules={validation.title}
      required
    />

    <FormField
      label="Catalog Number"
      id="catalog_number"
      bind:value={$form.catalog_number}
      error={$errors.catalog_number}
      rules={validation.catalog_number}
      required
    />

    <FormTextarea
      label="Description"
      id="description"
      bind:value={$form.description}
      error={$errors.description}
      rules={validation.description}
      required
    />

    <FormField
      label="Release Date"
      id="release_date"
      type="date"
      bind:value={$form.release_date}
      error={$errors.release_date}
      rules={validation.release_date}
      required
    />

    <FormField
      label="Price"
      id="price"
      type="number"
      bind:value={$form.price}
      error={$errors.price}
      rules={validation.price}
      required
    />

    <div class="flex justify-end gap-4 pt-6">
      <Button variant="outline" href="/releases">Cancel</Button>
      <Button type="submit">Save Changes</Button>
    </div>
  </Form>
</PageContainer>
