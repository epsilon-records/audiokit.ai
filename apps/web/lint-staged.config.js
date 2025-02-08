export default {
  '**/*.ts': () => 'tsc --noEmit',
  '**/*.{ts,js,md,svelte,css,html,json}': ['eslint --fix', 'prettier --write --list-different'],
};
