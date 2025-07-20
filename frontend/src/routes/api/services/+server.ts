import { CTF_CONFIG, saveConfig } from "$lib/server/config";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({}) => {
    return json(CTF_CONFIG.services);
};