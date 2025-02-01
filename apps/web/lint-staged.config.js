export default {
  '**/*.ts': () => 'bun x tsc --noEmit',

  '**/*.{ts,js,md,svelte,css,html,json}': ['bun x prettier --write --list-different', 'eslint'],
};
