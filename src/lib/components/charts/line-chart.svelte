<script lang="ts">
  import { Chart, type ChartConfiguration } from 'chart.js/auto';

  // Define the type for data points
  interface DataPoint {
    x: string;
    y: number;
  }

  // Use runes for props
  let data = $state<DataPoint[]>([
    { x: 'Jan', y: 10 },
    { x: 'Feb', y: 20 },
    { x: 'Mar', y: 30 },
  ]);
  let xAxis = $state<'x' | 'y'>('x');
  let yAxis = $state<'x' | 'y'>('y');
  let className = $state('');

  // State management
  let canvas = $state<HTMLCanvasElement | null>(null);
  let chart = $state<Chart | null>(null);

  // Create chart function
  function createChart() {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: data.map((d) => d[xAxis]),
        datasets: [
          {
            label: yAxis.charAt(0).toUpperCase() + yAxis.slice(1),
            data: data.map((d) => d[yAxis] as number),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    };

    chart = new Chart(ctx, config);
  }

  // Side effect to create and destroy chart
  $effect(() => {
    createChart();
    return () => {
      chart?.destroy();
    };
  });
</script>

<canvas bind:this={canvas} class={className}></canvas>
