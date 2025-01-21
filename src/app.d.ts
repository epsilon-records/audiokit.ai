// See https://svelte.dev/docs/kit/types#app.d.ts
declare global {
  namespace App {
    interface Locals {
      auth: import('@clerk/backend').Auth;
    }
  }
}

export {};
