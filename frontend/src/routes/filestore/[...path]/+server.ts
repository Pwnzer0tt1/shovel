import path from "node:path";
import fs from "node:fs";
import type { RequestHandler } from "@sveltejs/kit";
import { error } from "node:console";


export const GET: RequestHandler = ({ url }) => {
    const pathName = path.join("../suricata/output", url.pathname);

    try {
        const file = fs.readFileSync(pathName);
        return new Response(file);
    }
    catch {
        error(404);
    }
};