import type { ParamMatcher } from "@sveltejs/kit";

export const match = ((param: string) => {
    return true;
}) satisfies ParamMatcher;