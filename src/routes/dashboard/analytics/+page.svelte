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

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Analytics Dashboard</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Track your performance metrics, streaming data, and audience engagement across platforms.
    </p>
    <div class="mt-4 flex justify-end">
      <DateRangePicker date={dateRange} onSelect={(range: any) => (dateRange = range)} />
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
