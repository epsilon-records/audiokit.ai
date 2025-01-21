import { sentrySvelteKit } from '@sentry/sveltekit';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: process.env.VITEST
    ? {
        conditions: ['browser'],
      }
    : undefined,
  plugins: [
    sentrySvelteKit({
      sourceMapsUploadOptions: {
        org: 'epsilon-records',
        project: 'audiokit',
      },
    }),
    sveltekit(),
  ],
});
