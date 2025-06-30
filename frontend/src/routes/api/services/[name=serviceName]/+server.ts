import { saveServicesConfig } from "$lib/server/services-config";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const DELETE: RequestHandler = ({ locals, params }) => {
    if (!params.name) {
        return json({ error: "Service name is required." }, { status: 400 });
    }
    
    if (locals.ctfConfig.services.delete(params.name)) {
        saveServicesConfig(locals.ctfConfig.services);
        return json({ ok: true });
    }

    return error(404, { message: "Service not found." });
};