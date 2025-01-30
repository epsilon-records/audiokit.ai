<script lang="ts">
  import { Calendar as CalendarPrimitive } from 'bits-ui';
  import { cn } from '$lib/utils.js';

  type $$Props = CalendarPrimitive.GridHeadProps;

  interface Props {
    class?: $$Props['class'];
    children?: import('svelte').Snippet;
    [key: string]: any;
  }

  let { class: className = undefined, children, ...rest }: Props = $props();
</script>

<CalendarPrimitive.GridHead class={cn(className)} {...rest}>
  {@render children?.()}
</CalendarPrimitive.GridHead>
