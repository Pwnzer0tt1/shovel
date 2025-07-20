import { z } from "zod/v4";


export const flowsListFilters = z.object({
    ts_to: z.string().optional().default(String(1e16)),
    services: z.array(z.string()).optional(),
    app_proto: z.string().optional(),
    search: z.string().optional(),
    tags_require: z.array(z.string()).optional(),
    tags_deny: z.array(z.string()).optional()
});

export type FlowsListFilters = z.infer<typeof flowsListFilters>;

export type Flow = {
    id: string,
    ts_start: number,
    ts_end: number,
    dest_ipport: string,
    app_proto: string,
    tags: string,
    metadata: {
        flowints: {
            [key: string]: number
        },
        flowvars: {
            match: string
        }[]
    }
};
export type Flows = Flow[];

export type Tag = {
    tag: string,
    color: string
};
export type Tags = Tag[];

export const flowId = z.bigint();

export const ctfConfig = z.object({
    start_date: z.string(),
    tick_length: z.number(),
    refresh_rate: z.number(),
    default_ip: z.ipv4(),
    services: z.record(z.string(), z.object({
        ipports: z.array(z.string()),
        color: z.string()
    }))
});

export type CtfConfig = z.infer<typeof ctfConfig>;

export const addService = z.object({
    name: z.string(),
    color: z.string().regex(/^#([a-fA-F0-9]{2}){3}$/),
    serviceIP: z.ipv4(),
    ports: z.string()
});

export type AddService = z.infer<typeof addService>;

export const deleteService = z.object({
    name: z.string()
});

export type DeleteService = z.infer<typeof deleteService>;

export const editRefreshRate = z.object({
    refreshRate: z.int32().min(1)
});

export type EditRefreshRate = z.infer<typeof editRefreshRate>;