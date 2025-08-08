import { flowsListFilters } from "$lib/schema";
import { CTF_CONFIG } from "$lib/server/config";
import prisma from "$lib/server/prisma";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ url, locals }) => {
    const filters = url.searchParams.get("filters") ?? "{}";
    const parsed = flowsListFilters.safeParse(JSON.parse(filters));

    if (!parsed.success) {
        return error(400, JSON.stringify(parsed.error.issues));
    }

    let { ts_to, services, app_proto, search, tags_require, tags_deny } = parsed.data;

    let fsrvs = {};
    if (services) {
        if (services.length === 0) {
            // Filter flows related to no services
            for (const s of Object.values(CTF_CONFIG.services)) {
                for (const ipp of s.ipports) {
                    services.push(`${ipp.ip}:${ipp.port}`);
                }
            }
            fsrvs = {
                NOT: {
                    OR: [
                        {
                            src_ipport: { in: services }
                        },
                        {
                            dest_ipport: { in: services }
                        }
                    ]
                }
            };
        }
        else if (services.length > 0) {
            fsrvs = {
                OR: [
                    {
                        src_ipport: { in: services }
                    },
                    {
                        dest_ipport: { in: services }
                    }
                ]
            };
        }
    }
    
    let ftags_deny = {};
    if (tags_deny) {
        if (tags_deny.length > 0) {
            ftags_deny = {
                NOT: {
                    alerts: {
                        every: {
                            tag: { in: tags_deny }
                        }
                    }
                }
            };
        }
    }

    let ftags_req = {};
    if (tags_require) {
        if (tags_require.length > 0) {
            
            ftags_req = {
                alerts: {
                    every: {
                        tag: { in: tags_require }
                    }
                }
            };
        }
    }

    let search_fid = {};
    if (search) {
        const globs: { flow_id: bigint }[] = await prisma.$queryRaw`SELECT flow_id FROM raw WHERE REGEXP_LIKE(ENCODE("blob", 'escape'), ${search});`;
        search_fid = {
            id: { in: globs.map((v) => v.flow_id) }
        };
    }

    const flows = await prisma.flow.findMany({
        select: {
            id: true,
            ts_start: true,
            ts_end: true,
            dest_ip: true,
            dest_port: true,
            dest_ipport: true,
            app_proto: true,
            metadata: true,
            alerts: {
                select: {
                    tag: true
                }
            }
        },
        where: {
            AND: [
                {
                    ts_start: {
                        lte: Number(ts_to)
                    }
                },
                {
                    app_proto: {
                        equals: app_proto === "raw" ? "failed" : app_proto
                    }
                },
                fsrvs,
                ftags_deny,
                ftags_req,
                search_fid
            ]
        },
        orderBy: {
            ts_start: "desc"
        },
        take: 100
    });

    const prs = await prisma.flow.groupBy({
        by: "app_proto",
        where: {
            app_proto: {
                not: "failed"
            }
        }
    });

    const tags = await prisma.alert.groupBy({
        by: ["tag", "color"],
        orderBy: {
            color: "asc"
        }
    });

    let seFlows: any = [];
    for (let index = 0; index < flows.length; index += 1) {
        seFlows.push(flows[index]);
        seFlows[index].id = flows[index].id.toString();
        seFlows[index].ts_start = flows[index].ts_start?.toString();
        seFlows[index].ts_end = flows[index].ts_end?.toString();
    }

    return json({
        flows: seFlows,
        appProto: prs.map((v) => v.app_proto),
        tags
    });
};