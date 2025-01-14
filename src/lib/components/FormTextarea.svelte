<script lang="ts">
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import type { ValidationRule } from '$lib/utils/validation';
  import { validateField } from '$lib/utils/validation';

  let {
    label,
    id,
    value = '',
    placeholder = '',
    required = false,
    rules = [],
    rows = 4,
    class: className = '',
  } = $props<{
    label: string;
    id: string;
    value?: string;
    placeholder?: string;
    required?: boolean;
    rules?: ValidationRule[];
    rows?: number;
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

  <Textarea
    {id}
    {rows}
    {placeholder}
    bind:value
    on:blur={validate}
    class="bg-background resize-none"
    class:border-destructive={touched && error}
    aria-invalid={error ? 'true' : undefined}
    {required}
  />
</div>
