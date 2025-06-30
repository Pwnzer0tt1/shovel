import { PrismaClient } from "../../../../prisma_eve_db/eve_db/client";
import type { Database } from "better-sqlite3";
import * as BetterSqlit3 from "better-sqlite3";


export const prismaEveDb = new PrismaClient();


const DatabaseConstructor = BetterSqlit3.default;
export const betterEveDb: Database = new DatabaseConstructor("../suricata/output/eve.db");
betterEveDb.defaultSafeIntegers();
betterEveDb.pragma('journal_mode = WAL');