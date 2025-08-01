-- Migration copied from Prisma
-- CreateTable
CREATE TABLE "flow" (
    "id" BIGINT NOT NULL,
    "ts_start" BIGINT NOT NULL,
    "ts_end" BIGINT NOT NULL,
    "src_ip" TEXT NOT NULL,
    "src_port" INTEGER,
    "src_ipport" TEXT,
    "dest_ip" TEXT NOT NULL,
    "dest_port" INTEGER,
    "dest_ipport" TEXT,
    "pcap_filename" TEXT,
    "proto" TEXT NOT NULL,
    "app_proto" TEXT,
    "metadata" JSONB,
    "extra_data" JSONB,

    CONSTRAINT "flow_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "fileinfo" (
    "id" SERIAL NOT NULL,
    "flow_id" BIGINT NOT NULL,
    "timestamp" BIGINT NOT NULL,
    "extra_data" JSONB,

    CONSTRAINT "fileinfo_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app_event" (
    "id" SERIAL NOT NULL,
    "flow_id" BIGINT NOT NULL,
    "timestamp" BIGINT NOT NULL,
    "app_proto" TEXT NOT NULL,
    "extra_data" JSONB,

    CONSTRAINT "app_event_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "anomaly" (
    "id" SERIAL NOT NULL,
    "flow_id" BIGINT NOT NULL,
    "timestamp" BIGINT NOT NULL,
    "extra_data" JSONB,

    CONSTRAINT "anomaly_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "alert" (
    "id" SERIAL NOT NULL,
    "flow_id" BIGINT NOT NULL,
    "tag" TEXT,
    "color" TEXT,
    "timestamp" BIGINT NOT NULL,
    "extra_data" JSONB,

    CONSTRAINT "alert_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "raw" (
    "id" SERIAL NOT NULL,
    "flow_id" BIGINT NOT NULL,
    "count" INTEGER,
    "server_to_client" INTEGER,
    "blob" BYTEA,

    CONSTRAINT "raw_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "flow_ts_start_idx" ON "flow"("ts_start");

-- CreateIndex
CREATE INDEX "flow_app_proto_idx" ON "flow"("app_proto");

-- CreateIndex
CREATE INDEX "flow_src_ipport_idx" ON "flow"("src_ipport");

-- CreateIndex
CREATE INDEX "flow_dest_ipport_idx" ON "flow"("dest_ipport");

-- CreateIndex
CREATE INDEX "fileinfo_flow_id_idx" ON "fileinfo"("flow_id");

-- CreateIndex
CREATE UNIQUE INDEX "fileinfo_flow_id_timestamp_key" ON "fileinfo"("flow_id", "timestamp");

-- CreateIndex
CREATE INDEX "app_event_flow_id_idx" ON "app_event"("flow_id");

-- CreateIndex
CREATE UNIQUE INDEX "app_event_flow_id_app_proto_timestamp_key" ON "app_event"("flow_id", "app_proto", "timestamp");

-- CreateIndex
CREATE INDEX "anomaly_flow_id_idx" ON "anomaly"("flow_id");

-- CreateIndex
CREATE UNIQUE INDEX "anomaly_flow_id_timestamp_key" ON "anomaly"("flow_id", "timestamp");

-- CreateIndex
CREATE INDEX "alert_tag_idx" ON "alert"("tag");

-- CreateIndex
CREATE INDEX "alert_flow_id_idx" ON "alert"("flow_id");

-- CreateIndex
CREATE UNIQUE INDEX "alert_flow_id_tag_key" ON "alert"("flow_id", "tag");

-- CreateIndex
CREATE INDEX "raw_flow_id_idx" ON "raw"("flow_id");

-- CreateIndex
CREATE UNIQUE INDEX "raw_flow_id_count_key" ON "raw"("flow_id", "count");

-- Because Prisma Schema doesn't fully support generated columns raw SQL queries must be used.
-- PostgreSQL generated columns require immutable values which is not guaranteed by timestamp function.
CREATE FUNCTION set_ts_fn() RETURNS trigger AS $$
BEGIN
    UPDATE flow SET src_ipport = src_ip || (CASE WHEN src_port IS NULL THEN '' ELSE ':' || src_port END);
	UPDATE flow SET dest_ipport = dest_ip || (CASE WHEN dest_port IS NULL THEN '' ELSE ':' || dest_port END);

	RETURN new;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_ts AFTER INSERT ON flow FOR each ROW EXECUTE PROCEDURE set_ts_fn();


ALTER TABLE alert DROP COLUMN tag;
ALTER TABLE alert ADD COLUMN tag TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, tag, 0}') STORED;

ALTER TABLE alert DROP COLUMN color;
ALTER TABLE alert ADD COLUMN color TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, color, 0}') STORED;