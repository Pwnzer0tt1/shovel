import prisma from "$lib/server/prisma";
import { error, json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ params, locals }) => {
    if (!params.flow) {
        return json({ error: "Flow ID is required" }, { status: 400 });
    }

    // Query flow from database
    const flow = await prisma.flow.findUnique({
        select: {
            id: true,
            ts_start: true,
            ts_end: true,
            src_ipport: true,
            dest_ipport: true,
            dest_port: true,
            pcap_filename: true,
            proto: true,
            app_proto: true,
            metadata: true,
            extra_data: true
        },
        where: {
            id: BigInt(params.flow)
        }
    });

    if (flow === null) {
        return error(404);
    }

    let result: any = {
        flow: {
            ...flow,
            id: flow.id.toString(),
            ts_start: flow.ts_start.toString(),
            ts_end: flow.ts_end.toString()
        }
    };

    // Get associated fileinfos
    // See https://docs.suricata.io/en/suricata-7.0.10/file-extraction/file-extraction.html
    if (flow.app_proto) {
        if (["http", "http2", "smtp", "ftp", "nfs", "smb"].includes(flow.app_proto)) {
            const fileinfo = await prisma.fileinfo.findMany({
                select: {
                    extra_data: true
                },
                where: {
                    flow_id: BigInt(params.flow)
                },
                orderBy: {
                    id: "asc"
                }
            });

            result.fileinfo = fileinfo;
        }
    }

    // Get associated application layer(s) metadata
    if (result.flow.app_proto !== null && result.flow.app_proto !== "failed") {
        const appEvents = await prisma.app_event.findMany({
            select: {
                app_proto: true,
                extra_data: true
            },
            where: {
                flow_id: BigInt(params.flow)
            },
            orderBy: {
                id: "asc"
            }
        });

        for (const row of appEvents) {
            if (result[row.app_proto]) {
                result[row.app_proto].push(row.extra_data);
            }
            else {
                result[row.app_proto] = [row.extra_data];
            }
        }
    }

    // Get associated alert
    if (result.flow.extra_data.alerted) {
        result.alert = await prisma.alert.findMany({
            select: {
                extra_data: true,
                color: true
            },
            where: {
                flow_id: BigInt(params.flow)
            },
            orderBy: {
                id: "asc"
            }
        });
    }

    // Get associated anomalies
    result.anomaly = await prisma.anomaly.findMany({
        select: {
            extra_data: true
        },
        where: {
            flow_id: BigInt(params.flow)
        },
        orderBy: {
            id: "asc"
        }
    });

    return json(result);
};