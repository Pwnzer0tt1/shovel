import { betterEveDb, prismaEveDb } from "$lib/server/db/eve_db";
import { prismaPayloadDb } from "$lib/server/db/payload_db";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ url, locals }) => {
    let ts_to = url.searchParams.get("to");
    let services = url.searchParams.getAll("service");
    let app_proto = url.searchParams.get("app_proto");
    let search = url.searchParams.get("search");
    let tags_require = url.searchParams.getAll("tag_require");
    let tags_deny = url.searchParams.getAll("tag_deny");
    if (ts_to) {
        if (!Number(ts_to)) {
            return error(400);
        }
    }
    else {
        ts_to = String(1e16)
    }

    let query = `WITH fsrvs AS (SELECT value FROM json_each($services)),
                 ftags_req AS (SELECT value FROM json_each($tagsreq)),
                 ftags_deny AS (SELECT value FROM json_each($tagsdeny)),
                 fsearchfid AS (SELECT value FROM json_each($searchfid))
            SELECT id,
                   ts_start,
                   ts_end,
                   dest_ipport,
                   app_proto,
                   metadata,
                   (SELECT GROUP_CONCAT(tag) FROM alert WHERE flow_id = flow.id) AS tags
            FROM flow
            WHERE ts_start <= $tsto
              AND ($appproto = app_proto OR $appproto IS NULL)`;

    if (services.length === 1 && services[0] === "!") {
        // Filter flows related to no services
        query += " AND NOT (src_ipport IN fsrvs OR dest_ipport IN fsrvs)";

        let services_addr = [];
        for (const s of Object.values(locals.ctfConfig.services)) {
            let ipports = s.ipports || s;
            for (const ipport of ipports) {
                services_addr.push(ipport);
            }
        }

        services = services_addr;
    }
    else if (services.length > 0) {
        query += " AND (src_ipport IN fsrvs OR dest_ipport IN fsrvs)";
    }

    if (tags_deny.length > 0) {
        // No alert with at least a denied tag exists for this flow
        query += `
            AND NOT EXISTS (
                SELECT 1 FROM alert
                WHERE flow_id == flow.id AND alert.tag IN ftags_deny
            )`;
    }

    if (tags_require.length > 0) {
        // Relational division to get all flow_id matching all chosen tags
        query += `
            AND flow.id IN (
                SELECT flow_id FROM alert WHERE tag IN ftags_req GROUP BY flow_id
                HAVING COUNT(*) = (SELECT COUNT(*) FROM ftags_req)
            )`;
    }

    let search_fid = [];
    if (search) {
        let rows: any[] = betterEveDb.prepare("SELECT flow_id FROM raw WHERE blob GLOB ?;").all(`*${search}*`);
        for (const r of rows) {
            search_fid.push(r.flow_id);
        }

        query += " AND flow.id IN fsearchfid";
    }
    query += " ORDER BY ts_start DESC LIMIT 100";

    let rows: any[] = betterEveDb.prepare(query).all({
        services: JSON.stringify(services),
        tagsreq: JSON.stringify(tags_require),
        tagsdeny: JSON.stringify(tags_deny),
        tsto: Number(ts_to),
        appproto: app_proto === "raw" ? "failed" : app_proto,
        searchfid: JSON.stringify(search_fid)
    });

    let flows: any[] = [];
    for (const row of rows) {
        let flow = row;
        flow.id = flow.id.toString();
        flow.ts_start = flow.ts_start.toString();
        flow.ts_end = flow.ts_end.toString();
        flow.metadata = JSON.parse(flow.metadata);
        //flow.extra_data = JSON.parse(flow.extra_data);
        flows.push(flow);
    }

    // Fetch application protocols
    rows = await prismaEveDb.$queryRaw`SELECT DISTINCT app_proto FROM flow;`;
    let prs = [];
    for (const r of rows) {
        if (r.app_proto && r.app_proto !== "failed") {
            prs.push(r.app_proto);
        }
    }

    // Fetch tags
    let tags: any[] = await prismaEveDb.$queryRaw`SELECT tag, color FROM alert GROUP BY tag ORDER BY color`;
    
    return json({
        flows,
        appProto: prs,
        tags
    });
};