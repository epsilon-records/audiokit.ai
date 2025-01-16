<script lang="ts">
  import type { FieldValidation } from '$lib/utils/validation';
  import { validateForm } from '$lib/utils/validation';

  let { validation = {}, class: className = '' } = $props<{
    validation?: FieldValidation;
    class?: string;
  }>();

  let formElement: HTMLFormElement;
  let formData = $state<Record<string, any>>({});
  let errors = $state<Record<string, string>>({});

  function handleSubmit(event: Event) {
    event.preventDefault();
    errors = validateForm(formData, validation);

    if (Object.keys(errors).length === 0) {
      const submitEvent = new CustomEvent('submit', {
        detail: { formData },
      });
      formElement.dispatchEvent(submitEvent);
    }
  }
</script>

<form 
  bind:this={formElement} 
  onsubmit={handleSubmit} 
  class="space-y-6 {className}"
>
  {@render children({ formData, errors })}
</form>
