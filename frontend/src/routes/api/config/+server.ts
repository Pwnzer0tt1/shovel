import { json, type RequestHandler } from "@sveltejs/kit";
import { CTF_CONFIG } from "$lib/server/config";


export const GET: RequestHandler = () => {
    return json(CTF_CONFIG);
};