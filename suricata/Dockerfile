# Copyright (C) 2023-2024  ANSSI
# SPDX-License-Identifier: CC0-1.0
FROM rust:1.87.0-alpine3.22 AS builder
WORKDIR /src/
RUN apk add --no-cache musl-dev libpq-dev
COPY ./ /src/
RUN RUSTFLAGS="-C target-feature=-crt-static" cargo build --release

FROM alpine:3.22
RUN apk update
RUN apk add --no-cache suricata netcat-openbsd libpq-dev lua5.4-sql-postgres

COPY . /suricata
COPY --from=builder /src/target/release/libeve_postgres_output.so /suricata/
ENTRYPOINT ["/suricata/entrypoint.sh"]