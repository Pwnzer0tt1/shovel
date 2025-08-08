import { addService } from "$lib/schema";
import { CTF_CONFIG, saveConfig } from "$lib/server/config";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({}) => {
    return json(CTF_CONFIG.services);
};

export const POST: RequestHandler = async ({ request }) => {
    const res = addService.safeParse(await request.json());
    
    if (!res.success) {
        return error(400, { message: JSON.stringify(res.error.issues) });
    }

    if (CTF_CONFIG.services[res.data.name]) {
        delete CTF_CONFIG.services[res.data.name];
    }

    CTF_CONFIG.services[res.data.name] = {
        color: res.data.color,
        ipports: res.data.ipports
    };

    saveConfig(CTF_CONFIG);

    return json(CTF_CONFIG);
};

export const DELETE: RequestHandler = ({ url }) => {
    const name = url.searchParams.get("name");

    if (name === null) {
        return error(400, "A service name is required.");
    }

    if (CTF_CONFIG.services[name]) {
        delete CTF_CONFIG.services[name];
        saveConfig(CTF_CONFIG);
        return json(CTF_CONFIG);
    }
    
    return error(404, "Service not found.");
};