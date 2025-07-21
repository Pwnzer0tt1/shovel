-- Because Prisma Schema doesn't fully support generated columns raw SQL queries must be used.
-- PostgreSQL generated columns require immutable values which is not guaranteed by timestamp function.

create function set_ts_fn() returns trigger as $$
begin
	new.ts_start := extract(epoch from (extra_data->>'start')::timestamp)::bigint * 1000000 + extract(microseconds from (extra_data->>'start')::timestamp)::bigint;
	new.ts_end := extract(epoch from (extra_data->>'end')::timestamp)::bigint * 1000000 + extract(microseconds from (extra_data->>'end')::timestamp)::bigint;

	return new;
end
$$ language plpgsql;

create trigger set_ts after insert on flow for each row execute procedure set_ts_fn();


ALTER TABLE alert DROP COLUMN tag;
ALTER TABLE alert ADD COLUMN tag TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, tag, 0}') STORED;

ALTER TABLE alert DROP COLUMN color;
ALTER TABLE alert ADD COLUMN color TEXT GENERATED ALWAYS AS (extra_data#>>'{metadata, color, 0}') STORED;