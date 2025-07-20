import type { ParamMatcher } from "@sveltejs/kit";


export const match = ((param: string) => {
    if (param.length > 0) {
        // TODO: Check if service name exists
        return true;
    }
    else {
        return false;
    }
}) satisfies ParamMatcher;