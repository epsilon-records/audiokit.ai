<script lang="ts">
  import { Textarea } from '$lib/components/ui/textarea';

  let {
    label,
    id,
    value,
    error = '',
    required = false,
    minHeight = '200px',
  } = $props<{
    label: string;
    id: string;
    value: string;
    error?: string;
    required?: boolean;
    minHeight?: string;
  }>();
</script>

<div class="col-span-2">
  <label for={id} class="text-sm text-[#00ffff] uppercase mb-1 block">
    {label}{required ? ' *' : ''}
  </label>
  <Textarea
    {id}
    bind:value
    class="bg-background"
    style="min-height: {minHeight}"
    aria-invalid={error ? 'true' : undefined}
    {required}
  />
  {#if error}<span class="text-destructive text-sm">{error}</span>{/if}
</div>
