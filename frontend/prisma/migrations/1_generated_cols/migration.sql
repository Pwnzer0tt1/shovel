-- Because Prisma Schema doesn't fully support generated columns raw SQL queries must be used.
-- PostgreSQL generated columns require immutable values which is not guaranteed by timestamp function.

CREATE FUNCTION set_ts_fn() RETURNS trigger AS $$
BEGIN
	UPDATE flow SET ts_start = (extract(epoch FROM (new.extra_data->>'start')::TIMESTAMPTZ) * 1000000)::BIGINT;
	UPDATE flow SET ts_end = (extract(epoch FROM (new.extra_data->>'end')::TIMESTAMPTZ) * 1000000)::BIGINT;

	RETURN new;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_ts AFTER INSERT ON flow FOR each ROW EXECUTE PROCEDURE set_ts_fn();


ALTER TABLE alert DROP COLUMN tag;
ALTER TABLE alert ADD COLUMN tag TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, tag, 0}') STORED;

ALTER TABLE alert DROP COLUMN color;
ALTER TABLE alert ADD COLUMN color TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, color, 0}') STORED;