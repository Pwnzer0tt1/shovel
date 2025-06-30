import { PrismaClient } from "../../../../prisma_payload_db/payload_db/client";
import type { Database } from "better-sqlite3";
import * as BetterSqlit3 from "better-sqlite3";


export const prismaPayloadDb = new PrismaClient();


const DatabaseConstructor = BetterSqlit3.default;
export const betterPayloadDb: Database = new DatabaseConstructor("../suricata/output/payload.db");
betterPayloadDb.defaultSafeIntegers();
betterPayloadDb.pragma('journal_mode = WAL');