-- CreateTable
CREATE TABLE "raw" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "flow_id" INTEGER NOT NULL,
    "count" INTEGER,
    "server_to_client" INTEGER,
    "blob" BLOB
);

-- CreateIndex
CREATE INDEX "raw_flow_id_idx" ON "raw"("flow_id");

-- CreateIndex
Pragma writable_schema=1;
CREATE UNIQUE INDEX "sqlite_autoindex_raw_1" ON "raw"("flow_id", "count");
Pragma writable_schema=0;

