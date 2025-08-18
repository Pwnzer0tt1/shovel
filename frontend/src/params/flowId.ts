import { flowId } from "$lib/schema";
import type { ParamMatcher } from "@sveltejs/kit";


export const match = ((param: string) => {
    try {
        flowId.parse(BigInt(param));
        // TODO: Check if flowId exists in the database
        return true;
    }
    catch (e) {
        return false;
    }
}) satisfies ParamMatcher;