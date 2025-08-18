import prisma from "$lib/server/prisma";
import { json, type RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = async ({}) => {
    const flagsOut = await prisma.alert.findMany({
        select: {
            flow_id: true,
            timestamp: true
        },
        where: {
            tag: "FLAG OUT"
        }
    });
    const flowsNum = await prisma.flow.count();
    const flagsOutFlows = await prisma.flow.findMany({
        select: {
            ts_start: true,
            dest_ipport: true
        },
        where: {
            id: { in: flagsOut.map((v) => v.flow_id) }
        }
    });

    return json({
        flagsOut: flagsOut.map((v) => v.timestamp.toString()),
        flowsNum,
        flagsOutFlows: flagsOutFlows.map((v) => { return {ts_start: v.ts_start.toString(), dest_ipport: v.dest_ipport} })
    });
};