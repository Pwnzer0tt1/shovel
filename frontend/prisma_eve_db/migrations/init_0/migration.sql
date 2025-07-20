-- CreateTable
CREATE TABLE "alert" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "flow_id" INTEGER NOT NULL,
    "timestamp" INTEGER NOT NULL,
    "extra_data" TEXT
);

-- CreateTable
CREATE TABLE "anomaly" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "flow_id" INTEGER NOT NULL,
    "timestamp" INTEGER NOT NULL,
    "extra_data" TEXT
);

-- CreateTable
CREATE TABLE "app-event" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "flow_id" INTEGER NOT NULL,
    "timestamp" INTEGER NOT NULL,
    "app_proto" TEXT NOT NULL,
    "extra_data" TEXT
);

-- CreateTable
CREATE TABLE "fileinfo" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "flow_id" INTEGER NOT NULL,
    "timestamp" INTEGER NOT NULL,
    "extra_data" TEXT
);

-- CreateTable
CREATE TABLE "flow" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "src_ip" TEXT NOT NULL,
    "src_port" INTEGER,
    "dest_ip" TEXT NOT NULL,
    "dest_port" INTEGER,
    "pcap_filename" TEXT,
    "proto" TEXT NOT NULL,
    "app_proto" TEXT,
    "metadata" TEXT,
    "extra_data" TEXT
);

-- CreateIndex
CREATE INDEX "alert_flow_id_idx" ON "alert"("flow_id");

-- CreateIndex
CREATE INDEX "anomaly_flow_id_idx" ON "anomaly"("flow_id");

-- CreateIndex
Pragma writable_schema=1;
CREATE UNIQUE INDEX "sqlite_autoindex_anomaly_1" ON "anomaly"("flow_id", "timestamp");
Pragma writable_schema=0;

-- CreateIndex
CREATE INDEX "app-event_flow_id_idx" ON "app-event"("flow_id");

-- CreateIndex
Pragma writable_schema=1;
CREATE UNIQUE INDEX "sqlite_autoindex_app-event_1" ON "app-event"("flow_id", "app_proto", "timestamp");
Pragma writable_schema=0;

-- CreateIndex
CREATE INDEX "fileinfo_flow_id_idx" ON "fileinfo"("flow_id");

-- CreateIndex
Pragma writable_schema=1;
CREATE UNIQUE INDEX "sqlite_autoindex_fileinfo_1" ON "fileinfo"("flow_id", "timestamp");
Pragma writable_schema=0;

-- CreateIndex
CREATE INDEX "flow_app_proto_idx" ON "flow"("app_proto");

