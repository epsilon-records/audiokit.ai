/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/strict-type-checked',
    'plugin:@typescript-eslint/stylistic-type-checked',
    'plugin:svelte/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 2020,
    extraFileExtensions: ['.svelte'],
    project: ['./tsconfig.json'],
    tsconfigRootDir: __dirname,
  },
  env: {
    browser: true,
    es2017: true,
    node: true,
  },
  overrides: [
    {
      files: ['*.svelte'],
      parser: 'svelte-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser',
      },
    },
  ],
  rules: {
    // TypeScript specific rules
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/consistent-type-imports': [
      'error',
      { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
    ],
    '@typescript-eslint/no-import-type-side-effects': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/consistent-type-definitions': ['error', 'interface'],
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/no-unnecessary-condition': 'error',
    '@typescript-eslint/strict-boolean-expressions': 'error',

    // Svelte specific rules
    'svelte/valid-compile': 'error',
    'svelte/no-unused-svelte-ignore': 'error',
    'svelte/html-quotes': ['error', { prefer: 'double' }],
    'svelte/html-self-closing': 'error',
    'svelte/no-at-html-tags': 'error',
    'svelte/require-store-callbacks-use-set-param': 'error',
    'svelte/require-store-reactive-access': 'error',
    'svelte/valid-prop-names-in-kit-pages': 'error',
    'svelte/prefer-style-directive': 'error',
    'svelte/no-store-async': 'error',
    'svelte/no-reactive-literals': 'error',
    'svelte/no-reactive-functions': 'error',
    'svelte/no-dom-manipulating': 'error',

    // General best practices
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-alert': 'error',
    'no-debugger': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    eqeqeq: ['error', 'always'],
    curly: ['error', 'all'],
    'no-floating-decimal': 'error',
    'no-multi-spaces': 'error',
    'no-return-await': 'error',
    'require-await': 'error',
    'no-throw-literal': 'error',
    'prefer-promise-reject-errors': 'error',
    'no-param-reassign': 'error',
    'prefer-template': 'error',
    'spaced-comment': ['error', 'always'],
    'sort-imports': ['error', { ignoreDeclarationSort: true }],
  },
  settings: {
    // Ensure ESLint can find your Svelte components
    'svelte/typescript': () => require('typescript'),
  },
  // Ignore build artifacts and dependencies
  ignorePatterns: [
    'node_modules',
    '.svelte-kit',
    'build',
    'package',
    '*.cjs',
    '*.mjs',
    'vite.config.ts.timestamp-*',
    'static',
    'coverage',
    'playwright-report',
    'test-results',
  ],
};
