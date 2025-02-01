export default {
  '**/*.ts': () => 'tsc --noEmit',
  '**/*.{ts,js,md,svelte,css,html,json}': ['prettier --write --list-different', 'eslint --fix'],
};
