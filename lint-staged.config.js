/** @type {import('./lib/types').Configuration} */
export default {
  '**/*.{ts,js,md,svelte,css,html,json}': ['prettier --write --list-different'],
};
