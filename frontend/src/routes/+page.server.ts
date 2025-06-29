import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = ({ locals }) => {
    return {
        ctfConfig: locals.ctfConfig
    };
};