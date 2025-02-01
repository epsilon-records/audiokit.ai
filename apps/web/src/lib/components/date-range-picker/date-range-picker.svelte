<script lang="ts">
  import { Calendar } from '$lib/components/ui/calendar';
  import { Button } from '$lib/components/ui/button';
  import { Popover, PopoverContent, PopoverTrigger } from '$lib/components/ui/popover';
  import { CalendarIcon } from 'lucide-svelte';
  import { cn } from '$lib/utils';
  import { format } from 'date-fns';

  interface DateRange {
    start: Date | undefined;
    end: Date | undefined;
  }

  let {
    date,
    onSelect,
    className = '',
  } = $props<{
    date: DateRange;
    onSelect: (date: DateRange) => void;
    className?: string;
  }>();

  let isOpen = $state(false);

  function handleSelect(selectedDate: Date | undefined) {
    if (!selectedDate) return;

    if (!date.start || (date.start && date.end)) {
      date = {
        start: selectedDate,
        end: selectedDate,
      };
    } else {
      if (selectedDate < date.start) {
        date = {
          start: selectedDate,
          end: date.start,
        };
      } else {
        date = {
          start: date.start,
          end: selectedDate,
        };
      }
    }

    onSelect(date);
    if (date.start && date.end) {
      isOpen = false;
    }
  }
</script>

<div class={cn('grid gap-2', className)}>
  <Popover open={isOpen} onOpenChange={(open) => (isOpen = open)}>
    <PopoverTrigger asChild>
      <Button
        variant="outline"
        class={cn(
          'w-[300px] justify-start text-left font-normal',
          !date && 'text-muted-foreground'
        )}
      >
        <CalendarIcon class="mr-2 h-4 w-4" />
        {#if date?.start && date?.end}
          <span>
            {format(date.start, 'LLL dd, y')} - {format(date.end, 'LLL dd, y')}
          </span>
        {:else}
          <span>Pick a date range</span>
        {/if}
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0" align="start">
      <Calendar value={date?.start} />
    </PopoverContent>
  </Popover>
</div>
