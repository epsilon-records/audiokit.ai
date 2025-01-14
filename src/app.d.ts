// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import PocketBase from 'pocketbase';

declare global {
	namespace App {
		interface Locals {
			pb: PocketBase;
			user: any;
		}
	}
}

export {};
