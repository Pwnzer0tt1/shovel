import prisma from "$lib/server/prisma";
import { json, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = async ({ params, locals }) => {
    if (!params.flow) {
        return json({ error: "Flow ID is required" }, { status: 400 });
    }

    const raws = await prisma.raw.findMany({
        select: {
            server_to_client: true,
            blob: true
        },
        where: {
            flow_id: BigInt(params.flow)
        },
        orderBy: {
            count: "asc"
        }
    });

    let result: { server_to_client: string, data: string }[] = [];
    for (const r of raws) {
        if (r.server_to_client && r.blob) {
            result.push({
                server_to_client: r.server_to_client?.toString(),
                data: Buffer.from(r.blob).toString("base64")
            });
        }
    }
    
    return json(result);
};