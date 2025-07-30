// @generated automatically by Diesel CLI.

diesel::table! {
    _prisma_migrations (id) {
        #[max_length = 36]
        id -> Varchar,
        #[max_length = 64]
        checksum -> Varchar,
        finished_at -> Nullable<Timestamptz>,
        #[max_length = 255]
        migration_name -> Varchar,
        logs -> Nullable<Text>,
        rolled_back_at -> Nullable<Timestamptz>,
        started_at -> Timestamptz,
        applied_steps_count -> Int4,
    }
}

diesel::table! {
    alert (id) {
        id -> Int4,
        flow_id -> Int8,
        timestamp -> Int8,
        extra_data -> Nullable<Jsonb>,
        tag -> Nullable<Text>,
        color -> Nullable<Text>,
    }
}

diesel::table! {
    anomaly (id) {
        id -> Int4,
        flow_id -> Int8,
        timestamp -> Int8,
        extra_data -> Nullable<Jsonb>,
    }
}

diesel::table! {
    app_event (id) {
        id -> Int4,
        flow_id -> Int8,
        timestamp -> Int8,
        app_proto -> Text,
        extra_data -> Nullable<Jsonb>,
    }
}

diesel::table! {
    fileinfo (id) {
        id -> Int4,
        flow_id -> Int8,
        timestamp -> Int8,
        extra_data -> Nullable<Jsonb>,
    }
}

diesel::table! {
    flow (id) {
        id -> Int8,
        ts_start -> Nullable<Int8>,
        ts_end -> Nullable<Int8>,
        src_ip -> Text,
        src_port -> Nullable<Int4>,
        src_ipport -> Nullable<Text>,
        dest_ip -> Text,
        dest_port -> Nullable<Int4>,
        dest_ipport -> Nullable<Text>,
        pcap_filename -> Nullable<Text>,
        proto -> Text,
        app_proto -> Nullable<Text>,
        metadata -> Nullable<Jsonb>,
        extra_data -> Nullable<Jsonb>,
    }
}

diesel::table! {
    raw (id) {
        id -> Int4,
        flow_id -> Int8,
        count -> Nullable<Int4>,
        server_to_client -> Nullable<Int4>,
        blob -> Nullable<Bytea>,
    }
}

diesel::allow_tables_to_appear_in_same_query!(
    _prisma_migrations,
    alert,
    anomaly,
    app_event,
    fileinfo,
    flow,
    raw,
);
