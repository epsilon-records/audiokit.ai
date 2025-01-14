<script lang="ts">
  import { Label } from '$lib/components/ui/label';
  import { Input } from '$lib/components/ui/input';

  let {
    label,
    id,
    value,
    placeholder = '',
    error = '',
    required = false,
  } = $props<{
    label: string;
    id: string;
    value: string;
    placeholder?: string;
    error?: string;
    required?: boolean;
  }>();
</script>

<div class="space-y-2">
  <Label for={id}>{label}{required ? ' *' : ''}</Label>
  <Input
    {id}
    name={id}
    bind:value
    class="bg-background"
    {placeholder}
    aria-invalid={error ? 'true' : undefined}
    {required}
  />
  {#if error}<span class="text-destructive text-sm">{error}</span>{/if}
</div>
