import { betterEveDb, prismaEveDb } from "$lib/server/db/eve_db";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ params, locals }) => {
    if (!params.flow) {
        return json({ error: "Flow ID is required" }, { status: 400 });
    }

    // Query flow from database
    let flow: any = betterEveDb.prepare("SELECT id, ts_start, ts_end, src_ipport, dest_ipport, dest_port, pcap_filename, proto, app_proto, metadata, extra_data FROM flow WHERE id = ?").get(params.flow);
    if (!flow) {
        return error(404);
    }

    flow.id = flow.id.toString();
    flow.ts_start = flow.ts_start.toString();
    flow.ts_end = flow.ts_end.toString();
    flow.dest_port = flow.dest_port.toString();
    let result: any = {
        flow: flow
    };
    let app_proto = result.flow.app_proto;

    // Get associated fileinfo
    // See https://docs.suricata.io/en/suricata-6.0.9/file-extraction/file-extraction.html
    if (["http", "http2", "smtp", "ftp", "nfs", "smb"].includes(app_proto)) {
        let rows = betterEveDb.prepare("SELECT extra_data FROM fileinfo WHERE flow_id = ? ORDER BY id").all(params.flow);
        result.fileinfo = rows;
    }

    // Get associated application layer(s) metadata
    if (app_proto && app_proto !== "failed") {
        let rows: any[] = betterEveDb.prepare("SELECT app_proto, extra_data FROM 'app-event' WHERE flow_id = ? ORDER BY id").all(params.flow);
        for (const row of rows) {
            if (result[row.app_proto]) {
                result[row.app_proto].push(JSON.parse(row.extra_data || ""));
            }
            else {
                result[row.app_proto] = [JSON.parse(row.extra_data || "")];
            }
        }
    }

    // Get associated alert
    if (result.flow.alerted) {
        result.alert = betterEveDb.prepare("SELECT extra_data, color FROM alert WHERE flow_id = ? ORDER BY id").all(params.flow);
    }

    // Get associated anomalies
    result.anomaly = betterEveDb.prepare("SELECT extra_data FROM anomaly WHERE flow_id = ? ORDER BY id").all(params.flow);

    return json(result);
};