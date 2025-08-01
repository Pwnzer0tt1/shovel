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