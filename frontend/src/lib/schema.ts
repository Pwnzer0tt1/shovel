import { z } from "zod/v4";


export const getFlowList = z.object({
    ts_to: z.int(),
    services: z.array(z.string()),
    app_proto: z.string(),
    search: z.string(),
    tags_require: z.array(z.string()),
    tags_deny: z.array(z.string())
});