import type { Handle } from "@sveltejs/kit";
import "dotenv/config";


export const handle: Handle = async ({ event, resolve }) => {
    const response = await resolve(event);
    return response;
};