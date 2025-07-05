// See https://svelte.dev/docs/kit/types#app.d.ts

import type { CtfConfig } from "$lib/schema";

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			ctfConfig: CtfConfig
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
