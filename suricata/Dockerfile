FROM rust:1.87.0-alpine3.22 AS builder
WORKDIR /src/
RUN apk add --no-cache musl-dev libpq-dev
COPY ./ /src/
RUN RUSTFLAGS="-C target-feature=-crt-static" cargo build --release


FROM lua5.1-luarocks-alpine
RUN apk update
RUN apk add --no-cache suricata netcat-openbsd libpq-dev gcc musl-dev

RUN luarocks install pgmoon
RUN luarocks install luasocket

COPY . /suricata
COPY --from=builder /src/target/release/libeve_postgres_output.so /suricata/

ENTRYPOINT ["/suricata/entrypoint.sh"]