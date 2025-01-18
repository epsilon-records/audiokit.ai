<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { DateRangePicker } from '$lib/components/date-range-picker';
  import { LineChart } from '$lib/components/charts';

  let { data } = $props();

  let dateRange = $state({
    start: data.dateRange.start,
    end: data.dateRange.end,
  });

  $effect(() => {
    // Refresh data when date range changes
    console.log('Date range updated:', dateRange);
  });
</script>

<div class="space-y-4 p-4">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Analytics Dashboard</h1>
    <DateRangePicker date={dateRange} onSelect={(range: any) => (dateRange = range)} />
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <Card>
      <CardHeader>
        <CardTitle>Streaming Analytics</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data.streaming} xAxis="timestamp" yAxis="streams" />
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Social Media Growth</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data.social} xAxis="timestamp" yAxis="followers" />
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Revenue Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <LineChart data={data.revenue} xAxis="timestamp" yAxis="amount" />
      </CardContent>
    </Card>
  </div>
</div>
