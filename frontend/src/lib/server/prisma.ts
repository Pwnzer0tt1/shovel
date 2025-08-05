import { PrismaClient } from "../../generated/prisma/client";
import { DATABASE_URL } from "$env/static/private";


const prisma = new PrismaClient({
    datasourceUrl: DATABASE_URL
});

export default prisma;