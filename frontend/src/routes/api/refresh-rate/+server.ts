import { loadServicesConfig, saveServicesConfig } from "$lib/server/services-config";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({ locals }) => {
    // Get current refresh rate
    return json({ refresh_rate: locals.ctfConfig.refresh_rate })
};

export const POST: RequestHandler = async ({ locals, request }) => {
    // Update refresh rate
    let data = await request.json();
    let refresh_rate = Number(data.refresh_rate) || 120;

    if (refresh_rate < 1) {
        return error(400, { message: "Refresh rate must be at least 1 second." });
    }

    locals.ctfConfig.refresh_rate = refresh_rate;

    return json({ success: true, refresh_rate: refresh_rate });
};