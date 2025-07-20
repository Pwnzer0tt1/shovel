import { betterPayloadDb } from "$lib/server/db/payload_db";
import { json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({ params, locals }) => {
    if (!params.flow) {
        return json({ error: "Flow ID is required" }, { status: 400 });
    }

    let rows: any[] = betterPayloadDb.prepare("SELECT server_to_client, blob FROM raw WHERE flow_id = ? ORDER BY count").all(params.flow);

    let result: any = [];
    for (const r of rows) {
        result.push({
            server_to_client: r.server_to_client.toString(),
            data: Buffer.from(r.blob).toString("base64")
        });
    }
    
    return json(result);
};