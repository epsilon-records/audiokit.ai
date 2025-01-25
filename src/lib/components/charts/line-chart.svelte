<script lang="ts">
  import { Chart, type ChartConfiguration, registerables } from 'chart.js';
  import { fade } from 'svelte/transition';

  Chart.register(...registerables);

  // Define the type for data points
  interface DataPoint {
    x: string | number;
    y: number;
  }

  // Use runes for props
  let data = $state<DataPoint[]>([]);
  let xAxisKey = $state<keyof DataPoint>('x');
  let yAxisKey = $state<keyof DataPoint>('y');
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
  $effect(() => {
    if (!canvas || !data.length) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: data.map((d) => d[xAxisKey]),
        datasets: [
          {
            label: title || String(yAxisKey),
            data: data.map((d) => d[yAxisKey]),
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

    chart = new Chart(canvas, config);

    return () => {
      chart?.destroy();
    };
  });
</script>

<canvas bind:this={canvas} class={className} in:fade={{ duration: 500 }}></canvas>
