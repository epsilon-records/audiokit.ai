import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    // adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
    // If your environment is not supported, or you settled on a specific environment, switch out the adapter.
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter({
      // Runtime configuration
      runtime: 'edge', // 'edge' or 'nodejs' (default: 'nodejs')

      // Regions configuration
      regions: ['fra1'], // Optional: specify Vercel regions (default: auto-detected)

      // Edge middleware configuration
      edgeMiddleware: true, // Optional: enable edge middleware (default: false)
    }),
  },
};

export default config;
