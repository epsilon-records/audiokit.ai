import { sentrySvelteKit } from '@sentry/sveltekit';
import { sveltekit } from '@sveltejs/kit/vite';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    sentrySvelteKit({
      sourceMapsUploadOptions: {
        org: 'epsilon-records',
        project: 'audiokit',
        telemetry: false,
      },
    }),
    sveltekit(),
    visualizer({
      emitFile: true,
      filename: 'stats.html',
    }),
  ],
});
