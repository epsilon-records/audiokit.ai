<script lang="ts">
  import { Label } from '$lib/components/ui/label';
  import { Input } from '$lib/components/ui/input';
  import type { ValidationRule } from '$lib/utils/validation';
  import { validateField } from '$lib/utils/validation';

  let {
    label,
    id,
    type = 'text',
    value = '',
    placeholder = '',
    required = false,
    rules = [],
    class: className = '',
  } = $props<{
    label: string;
    id: string;
    type?: string;
    value?: string;
    placeholder?: string;
    required?: boolean;
    rules?: ValidationRule[];
    class?: string;
  }>();

  let touched = $state(false);
  let error = $state<string | null>(null);

  function validate() {
    touched = true;
    error = validateField(value, rules);
  }
</script>

<div class="space-y-2 {className}">
  <Label for={id} class="flex justify-between">
    <span>{label}{required ? ' *' : ''}</span>
    {#if touched && error}
      <span class="text-destructive text-sm">{error}</span>
    {/if}
  </Label>

  <Input
    {id}
    {type}
    {placeholder}
    bind:value
    on:blur={validate}
    class="bg-background"
    aria-invalid={error ? 'true' : undefined}
    {required}
  />
</div>
