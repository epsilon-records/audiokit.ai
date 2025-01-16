import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		alias: {
			// Explicitly mark Node.js built-ins as external
			'node:dns/promises': 'virtual:dns-promises'
		}
	},
	build: {
		rollupOptions: {
			external: [
				// Mark Node.js built-ins as external during build
				/^node:.*/
			]
		}
	}
});
