<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Chart, type ChartConfiguration } from 'chart.js/auto';

  let { data, xAxis, yAxis, className = '' } = $props();
  let canvas: HTMLCanvasElement;
  let chart: Chart;

  function createChart() {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: data.map((d) => d[xAxis]),
        datasets: [
          {
            label: yAxis.charAt(0).toUpperCase() + yAxis.slice(1),
            data: data.map((d) => d[yAxis]),
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

  $effect(() => {
    if (chart) {
      chart.data.labels = data.map((d) => d[xAxis]);
      chart.data.datasets[0].data = data.map((d) => d[yAxis]);
      chart.update();
    }
  });

  onMount(() => {
    createChart();
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });
</script>

<div class="w-full h-[300px] {className}">
  <canvas bind:this={canvas}></canvas>
</div>
