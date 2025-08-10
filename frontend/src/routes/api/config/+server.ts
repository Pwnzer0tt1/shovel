import { error, json, type RequestHandler } from "@sveltejs/kit";
import { CTF_CONFIG, saveConfig } from "$lib/server/config";
import { newCtfConfig } from "$lib/schema";


export const GET: RequestHandler = () => {
    return json(CTF_CONFIG);
};

export const POST: RequestHandler = async ({ request }) => {
    const res = newCtfConfig.safeParse(await request.json());

    if (!res.success) {
        return error(400, { message: JSON.stringify(res.error.issues) });
    }

    CTF_CONFIG.start_date = res.data.start_date;
    CTF_CONFIG.tick_length = res.data.tick_length;
    CTF_CONFIG.refresh_rate = res.data.refresh_rate;

    saveConfig(CTF_CONFIG);

    return json(CTF_CONFIG);
};