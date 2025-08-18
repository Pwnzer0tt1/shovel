import { PrismaClient } from "../../generated/prisma/client";
import { env } from "$env/dynamic/private";


const prisma = new PrismaClient({
    datasourceUrl: env.DATABASE_URL ?? "postgresql://postgres@postgres:5432/postgres"
});

export default prisma;