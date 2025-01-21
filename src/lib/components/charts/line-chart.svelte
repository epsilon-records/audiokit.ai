<script lang="ts">
  import { Chart, type ChartConfiguration } from 'chart.js/auto';
  import { fade } from 'svelte/transition';

  // Define the type for data points
  interface DataPoint {
    x: string;
    y: number;
  }

  // Use runes for props
  let data = $state<DataPoint[]>([]);
  let xAxis = $state<'x' | 'y'>('x');
  let yAxis = $state<'x' | 'y'>('y');
  let className = $state('');
  let title = $state('');
  let color = $state('#4F46E5');
  let showGrid = $state(true);
  let showLegend = $state(true);
  let animate = $state(true);
  let tension = $state(0.4);
  let fill = $state(true);

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
            label: title || yAxis.charAt(0).toUpperCase() + yAxis.slice(1),
            data: data.map((d) => d[yAxis] as number),
            borderColor: color,
            backgroundColor: fill ? `${color}20` : undefined,
            fill,
            tension,
            borderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: 'white',
            pointBorderColor: color,
            pointHoverBackgroundColor: color,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: animate ? 1000 : 0,
          easing: 'easeInOutQuart',
        },
        plugins: {
          legend: {
            display: showLegend,
            position: 'top',
          },
        },
        scales: {
          x: {
            grid: {
              display: showGrid,
              color: '#e2e8f0',
            },
            ticks: {
              font: {
                family: 'Inter',
              },
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              display: showGrid,
              color: '#e2e8f0',
            },
            ticks: {
              font: {
                family: 'Inter',
              },
            },
          },
        },
        interaction: {
          intersect: false,
          mode: 'index',
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

<canvas bind:this={canvas} class={className} in:fade={{ duration: 500 }}></canvas>
