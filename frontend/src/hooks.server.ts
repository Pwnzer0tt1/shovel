import type { Handle } from "@sveltejs/kit";
import "dotenv/config";


let CTF_CONFIG = {
    start_date: "1970-01-01T00:00+00:00",
    tick_length: 120,
    refresh_rate: 120,
    default_ip: "",
    services: new Map()
};


export const handle: Handle = async ({ event, resolve }) => {
    event.locals.ctfConfig = CTF_CONFIG;

    const response = await resolve(event);
    return response;
};