import svelteParser from 'svelte-eslint-parser';
import typescriptParser from '@typescript-eslint/parser';
import sveltePlugin from 'eslint-plugin-svelte';
import typescriptPlugin from '@typescript-eslint/eslint-plugin';

export default [
  {
    files: ['apps/web/src/**/*.js', 'apps/web/src/**/*.ts', 'apps/web/src/**/*.svelte'],
    ignores: ['**/node_modules/**'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      parser: typescriptParser,
      parserOptions: {
        extraFileExtensions: ['.svelte'],
        project: './tsconfig.json'
      }
    },
    plugins: {
      '@typescript-eslint': typescriptPlugin,
      svelte: sveltePlugin
    },
    rules: {
      // ... existing rules ...
    },
    settings: {
      'svelte/typescript': () => import('typescript')
    }
  },
  {
    files: ['apps/web/src/**/*.svelte'],
    ignores: ['**/node_modules/**'],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        parser: typescriptParser
      }
    }
  }
]; 