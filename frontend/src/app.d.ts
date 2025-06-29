// See https://svelte.dev/docs/kit/types#app.d.ts
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
				services: any
			}
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
