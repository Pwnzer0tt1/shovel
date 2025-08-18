import { CTF_CONFIG } from "$lib/server/config";
import type { PageServerLoad } from "./$types";


export const load: PageServerLoad = async ({}) => {
    return {
        ctfConfig: CTF_CONFIG
    };
};