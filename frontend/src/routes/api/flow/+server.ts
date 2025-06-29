import { prismaEveDb } from "$lib/server/db/eve_db";
import { prismaPayloadDb } from "$lib/server/db/payload_db";
import { json, type RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = async ({ url, locals }) => {
    let ts_to = url.searchParams.get("to");
    let services = url.searchParams.getAll("service");
    let app_proto = url.searchParams.get("app_proto");
    let search = url.searchParams.get("search");
    let tags_require = url.searchParams.getAll("tag_require");
    let tags_deny = url.searchParams.getAll("tag_deny");

    let query = `WITH fsrvs AS (SELECT value FROM json_each(?1)),
                 ftags_req AS (SELECT value FROM json_each(?2)),
                 ftags_deny AS (SELECT value FROM json_each(?3)),
                 fsearchfid AS (SELECT value FROM json_each(?6))
            SELECT id,
                   ts_start,
                   ts_end,
                   dest_ipport,
                   app_proto,
                   metadata,
                   (SELECT GROUP_CONCAT(tag) FROM alert WHERE flow_id = flow.id) AS tags
            FROM flow
            WHERE ts_start <= ?4
              AND (?5 = app_proto OR ?5 IS NULL)`;

    if (services.length === 1 && services[0] === "!") {
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
        query += `
            AND NOT EXISTS (
                SELECT 1 FROM alert
                WHERE flow_id == flow.id AND alert.tag IN ftags_deny
            )`;
    }

    if (tags_require.length > 0) {
        query += `
            AND flow.id IN (
                SELECT flow_id FROM alert WHERE tag IN ftags_req GROUP BY flow_id
                HAVING COUNT(*) = (SELECT COUNT(*) FROM ftags_req)
            )`;
    }

    let search_fid = [];
    if (search) {
        let result: any[] = await prismaPayloadDb.$queryRawUnsafe("SELECT flow_id FROM raw WHERE blob GLOB ?1;", `*${search}*`);
        for (const r of result) {
            search_fid.push(r.flow_id);
        }

        query += " AND flow.id IN fsearchfid";
    }
    query += " ORDER BY ts_start DESC LIMIT 100";


    let result: any[] = await prismaEveDb.$queryRawUnsafe(
        query,
        JSON.stringify(services),
        JSON.stringify(tags_require),
        JSON.stringify(tags_deny),
        Number(ts_to),
        app_proto === "raw" ? "failed" : app_proto,
        JSON.stringify(search_fid)
    );

    let flows: any[] = [];
    for (const row of result) {
        let flow = row;
        flow.metadata = JSON.parse(flow.metdata);
        //flow.extra_data = JSON.parse(flow.extra_data);
    }

    result = await prismaEveDb.$queryRaw`SELECT DISTINCT app_proto FROM flow;`;
    
    let prs = [];
    for (const r of result) {
        if (r.app_proto && r.app_proto !== "failed") {
            prs.push(r.app_proto);
        }
    }

    let tags: any[] = await prismaEveDb.$queryRaw`SELECT tag, color FROM alert GROUP BY tag ORDER BY color`;
    
    return json({
        flows,
        appProto: prs,
        tags
    });
};