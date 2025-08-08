import path from "node:path";
import fs from "node:fs";
import { error, type RequestHandler } from "@sveltejs/kit";


export const GET: RequestHandler = ({ url }) => {
    const pathName = path.join("../", url.pathname);

    try {
        const file = fs.readFileSync(pathName);
        return new Response(file);
    }
    catch {
        error(404);
    }
};