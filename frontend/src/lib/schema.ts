import { z } from "zod/v4";


export const getFlowList = z.object({
    ts_to: z.int(),
    services: z.array(z.string()),
    app_proto: z.string(),
    search: z.string(),
    tags_require: z.array(z.string()),
    tags_deny: z.array(z.string())
});

export const flowId = z.bigint();

export const servicesConfig = z.map(
    z.string(),
    z.object({
        ipports: z.array(z.string()),
        color: z.string()
    })
);

export type ServicesConfig = z.infer<typeof servicesConfig>;