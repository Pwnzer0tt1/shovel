import fs from "node:fs";
import { betterEveDb } from "$lib/server/db/eve_db";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({ params, locals }) => {
    if (!params.flow) {
        return json({ error: "Flow ID is required" }, { status: 400 });
    }

    // Get HTTP events
    let rows: any[] = betterEveDb.prepare("SELECT flow_id, extra_data FROM 'app-event' WHERE flow_id = ? AND app_proto = 'http' ORDER BY id").all(params.flow);

    // For each HTTP request, load client payload if it exists
    let data = [];
    for (const [tx_id, row] of Object.entries(rows)) {
        let req = row;
        //row.metadata = JSON.parse(row.metadata);
        req.extra_data = JSON.parse(row.extra_data);

        req.rq_content = null;

        if (req.http_method === "POST") {
            // First result should be the request
            let fileinfo_first_event: any = betterEveDb.prepare("SELECT extra_data FROM fileinfo WHERE flow_id = ? AND extra_data->>'tx_id' = ? ORDER BY id").get(params.flow, tx_id);
            if (!fileinfo_first_event) {
                return error(404);
            }
            
            let sha256 = JSON.parse(fileinfo_first_event.extra_data).sha256;
            if (!sha256) {
                return error(500);
            }

            // Load file
            let path = `../suricata/output/filestore/${sha256.slice(2)}/${sha256}`;
            const f = fs.readFileSync(path, "binary");
            req.rq_content = f;
        }
        
        data.push(req);
    }

    

    return json({});
};