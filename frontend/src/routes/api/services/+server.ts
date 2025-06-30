import { saveServicesConfig } from "$lib/server/services-config";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({ locals }) => {
    return json(locals.ctfConfig.services);
};

export const POST: RequestHandler = async ({ locals, request, url }) => {
    // Add or update a aservice
    let data = await request.json();
    let name = data.name;
    let old_name = data.old_name;
    let ipports = data.ipports || [];
    let color = data.color || "#007bff"; // default blue

    if (!name) {
        return error(400, { message: "Name is required." });
    }

    if (old_name && old_name !== name && locals.ctfConfig.services.get(old_name)) {
        locals.ctfConfig.services.delete(old_name);
    }

    locals.ctfConfig.services.set(name, {
        ipports: ipports,
        color: color
    });

    saveServicesConfig(locals.ctfConfig.services);

    return json({ ok: true, service: name });
};