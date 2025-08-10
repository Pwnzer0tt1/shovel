import { z } from "zod/v4";


export const flowsListFilters = z.object({
    ts_to: z.string().optional().default(String(1e16)),
    services: z.array(z.string()).optional(),
    app_proto: z.string().optional(),
    search: z.string().optional(),
    tags_require: z.array(z.string()),
    tags_deny: z.array(z.string())
});

export type FlowsListFilters = z.infer<typeof flowsListFilters>;

export type Flow = {
    id: string,
    ts_start: string,
    ts_end: string,
    src_ip: string,
    src_port: number | null,
    src_ipport: string,
    dest_ip: string,
    dest_port: number | null,
    dest_ipport: string,
    pcap_filename: string,
    proto: string,
    app_proto: string | null,
    tags: string,
    metadata: {
        flowints?: {
            [key: string]: number
        },
        flowvars?: {
            match: string
        }[],
        flowbits?: string[]
    } | null,
    extra_data: {
        pkts_toserver: number,
        pkts_toclient: number,
        bytes_toserver: number,
        bytes_toclient: number,
        bypassed: {
            pkts_toserver: number,
            pkts_toclient: number,
            bytes_toserver: number,
            bytes_toclient: number
        },
        start: string,
        end: string,
        age: number,
        bypass: string,
        state: string,
        reason: string,
        alerted: boolean
    } | null,
    alerts?: { tag: string }[]
};
export type Flows = Flow[];

export type Tag = {
    tag: string,
    color: string
};
export type Tags = Tag[];

export const flowId = z.bigint();

export const ctfConfig = z.object({
    start_date: z.iso.datetime({ local: true }),
    tick_length: z.number(),
    refresh_rate: z.number(),
    services: z.record(z.string(), z.object({
        ipports: z.array(z.object({
            ip: z.ipv4(),
            port: z.int32()
        })),
        color: z.string()
    }))
});

export type CtfConfig = z.infer<typeof ctfConfig>;

export const newCtfConfig = z.object({
    start_date: z.iso.datetime({ local: true }),
    tick_length: z.int().min(1),
    refresh_rate: z.int().min(1)
});

export type NewCtfConfig = z.infer<typeof newCtfConfig>;


export const addService = z.object({
    name: z.string(),
    color: z.string().regex(/^#([a-fA-F0-9]{2}){3}$/),
    ipports: z.array(z.object({
        ip: z.ipv4(),
        port: z.int32()
    })).min(1)
});

export type AddService = z.infer<typeof addService>;

export const editRefreshRate = z.object({
    refreshRate: z.int32().min(1)
});

export type EditRefreshRate = z.infer<typeof editRefreshRate>;