import { z } from "zod/v4";


export const getFlowList = z.object({
    ts_to: z.int(),
    services: z.array(z.string()),
    app_proto: z.string(),
    search: z.string(),
    tags_require: z.array(z.string()),
    tags_deny: z.array(z.string())
});

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

export const servicesConfig = z.map(
    z.string(),
    z.object({
        ipports: z.array(z.string()),
        color: z.string()
    })
);

export type ServicesConfig = z.infer<typeof servicesConfig>;

export type CtfConfig = {
    start_date: string,
	tick_length: number,
	refresh_rate: number,
	default_ip: string,
	services: ServicesConfig
};