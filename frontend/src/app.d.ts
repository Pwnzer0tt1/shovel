// See https://svelte.dev/docs/kit/types#app.d.ts

import type { ServicesConfig } from "$lib/schema";

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			ctfConfig: {
				start_date: string,
				tick_length: number,
				refresh_rate: number,
				default_ip: string,
				services: ServicesConfig
			}
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
