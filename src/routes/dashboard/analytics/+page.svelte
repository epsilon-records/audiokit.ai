<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { DateRangePicker } from '$lib/components/date-range-picker';
  import { LineChart } from '$lib/components/charts';
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from '$lib/components/ui/select';
  import { Button } from '$lib/components/ui/button';
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
  import { Calendar, Filter, RefreshCw } from 'lucide-svelte';

  let { data } = $props();

  let dateRange = $state({
    start: data.dateRange.start,
    end: data.dateRange.end,
  });

  let platform = $state('all');
  let interval = $state('daily');
  let comparison = $state('previous_period');

  const platforms = [
    { value: 'all', label: 'All Platforms' },
    { value: 'spotify', label: 'Spotify' },
    { value: 'apple_music', label: 'Apple Music' },
    { value: 'youtube_music', label: 'YouTube Music' },
  ];

  const intervals = [
    { value: 'hourly', label: 'Hourly' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
  ];

  const comparisons = [
    { value: 'previous_period', label: 'Previous Period' },
    { value: 'previous_year', label: 'Previous Year' },
    { value: 'none', label: 'No Comparison' },
  ];
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Analytics Dashboard</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Track your performance metrics, streaming data, and audience engagement across platforms.
    </p>
  </div>

  <div class="flex flex-wrap gap-4 mb-8">
    <DateRangePicker date={dateRange} onSelect={(range) => (dateRange = range)} />

    <Select value={platform} onValueChange={(value) => (platform = value)}>
      <SelectTrigger class="w-[180px]">
        <SelectValue placeholder="Select Platform" />
      </SelectTrigger>
      <SelectContent>
        {#each platforms as p}
          <SelectItem value={p.value}>{p.label}</SelectItem>
        {/each}
      </SelectContent>
    </Select>

    <Select value={interval} onValueChange={(value) => (interval = value)}>
      <SelectTrigger class="w-[150px]">
        <SelectValue placeholder="Select Interval" />
      </SelectTrigger>
      <SelectContent>
        {#each intervals as i}
          <SelectItem value={i.value}>{i.label}</SelectItem>
        {/each}
      </SelectContent>
    </Select>

    <Select value={comparison} onValueChange={(value) => (comparison = value)}>
      <SelectTrigger class="w-[180px]">
        <SelectValue placeholder="Select Comparison" />
      </SelectTrigger>
      <SelectContent>
        {#each comparisons as c}
          <SelectItem value={c.value}>{c.label}</SelectItem>
        {/each}
      </SelectContent>
    </Select>

    <Button variant="outline" class="gap-2">
      <RefreshCw class="w-4 h-4" />
      Refresh
    </Button>
  </div>

  <Tabs defaultValue="overview" class="space-y-4">
    <TabsList>
      <TabsTrigger value="overview">Overview</TabsTrigger>
      <TabsTrigger value="streaming">Streaming</TabsTrigger>
      <TabsTrigger value="engagement">Engagement</TabsTrigger>
      <TabsTrigger value="revenue">Revenue</TabsTrigger>
    </TabsList>

    <TabsContent value="overview">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader
            class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900"
          >
            <CardTitle>Total Streams</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <LineChart
              data={data.streaming}
              xAxis="timestamp"
              yAxis="streams"
              title="Streams Over Time"
              color="#3B82F6"
              className="h-[300px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900"
          >
            <CardTitle>Listener Growth</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <LineChart
              data={data.streaming}
              xAxis="timestamp"
              yAxis="listeners"
              title="Monthly Listeners"
              color="#8B5CF6"
              className="h-[300px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900"
          >
            <CardTitle>Revenue</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <LineChart
              data={data.revenue}
              xAxis="timestamp"
              yAxis="amount"
              title="Revenue Growth"
              color="#10B981"
              className="h-[300px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            class="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900"
          >
            <CardTitle>Social Engagement</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <LineChart
              data={data.social}
              xAxis="timestamp"
              yAxis="engagement"
              title="Social Engagement"
              color="#F97316"
              className="h-[300px]"
            />
          </CardContent>
        </Card>
      </div>
    </TabsContent>

    <!-- Add similar TabsContent sections for streaming, engagement, and revenue tabs -->
  </Tabs>
</div>
