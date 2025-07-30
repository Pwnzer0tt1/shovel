// Copyright (C) 2024  ANSSI
// SPDX-License-Identifier: GPL-2.0-or-later

use diesel::{Connection, ConnectionError, PgConnection, QueryResult, RunQueryDsl};
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};
use std::collections::HashMap;
use std::sync::Mutex;

use crate::models::{NewAlert, NewAnomaly, NewAppEvent, NewFileinfo, NewFlow};
use crate::schema::{alert, anomaly, app_event, fileinfo, flow};

const MIGRATIONS: EmbeddedMigrations = embed_migrations!();

lazy_static::lazy_static! {
    static ref FLOW_PCAP: Mutex<HashMap<i64, String>> = Mutex::new(HashMap::new());
}

/// Add one Eve event to the SQL database
fn write_event(conn: &mut PgConnection, buf: &str) -> QueryResult<usize> {
    // Parse EVE JSON to untyped JSON object
    // After some benchmarks, it was concluded that serde_json parsing is around 30x faster than regex_lite (crate originally used in shovel) captures.
    // regex create is generally faster compared to serde_json (1.5x-2x times) but having an already parsed JSON is more convinient.
    // Parsing to generic type serde_json::Value is slower than parsing into a typed struct
    // TODO: Create struct for parsing EVE JSON format
    let Ok(eve_json): Result<serde_json::Value, serde_json::Error> = serde_json::from_str(buf) else {
        log::warn!("Failed to parse EVE JSON.");
        return Ok(0);
    };

    // Ignore events that don't have event_type field, such as stats.
    let event_type = match eve_json.get("event_type") {
        Some(v) => v.as_str().unwrap(),
        None => return Ok(0)
    };

    let timestamp = chrono::DateTime::parse_from_str(eve_json.get("timestamp").expect("Missing timestamp.").as_str().unwrap(), "%Y-%m-%dT%H:%M:%S%.6f%z").unwrap().timestamp_micros();
    let flow_id = match eve_json.get("flow_id") {
        Some(v) => v.as_i64().unwrap(),
        None => return Ok(0)
    };

    // HACK: collect pcap_filename from app events, then use it later when writing flow event.
    // `pcap_filename` pointed by flow events seem wrong, this is maybe a Suricata bug.
    if event_type != "flow" {
        if let Some(pcap_filename) = eve_json.get("pcap_filename") {
            if let Ok(ref mut m) = FLOW_PCAP.try_lock() {
                m.insert(flow_id, pcap_filename.to_string());
            }
            else {
                log::warn!("Failed to lock FLOW_PCAP mutex, skipping insertion.");
            }
        }
    }

    match event_type {
        "flow" => {
            let src_ip = eve_json.get("src_ip").expect("Missing src_ip").to_string();
            let src_port: Option<i32> = match eve_json.get("src_port") {
                Some(v) => Some(v.as_i64().unwrap().try_into().unwrap()),
                None => None
            };
            let dest_ip = eve_json.get("dest_ip").expect("Missing dest_ip").to_string();
            let dest_port: Option<i32> = match eve_json.get("dest_port") {
                Some(v) => Some(v.as_i64().unwrap().try_into().unwrap()),
                None => None
            };
            
            let flow_pcap_local = FLOW_PCAP.lock().unwrap();
            let pcap_filename = match flow_pcap_local.get(&flow_id) {
                Some(v) => Some(v.clone()),
                None => match eve_json.get("pcap_filename") {
                    Some(p) => Some(p.to_string()),
                    None => Some("".to_string())
                }
            };

            let proto = eve_json.get("proto").unwrap().to_string();
            let app_proto = match eve_json.get("app_proto") {
                Some(v) => Some(v.to_string()),
                None => None
            };
            let metadata = eve_json.get("metadata").cloned();
            let extra_data = eve_json.get("flow").cloned();

            let new_flow = NewFlow {
                id: flow_id,
                src_ip,
                src_port,
                dest_ip,
                dest_port,
                pcap_filename,
                proto,
                app_proto,
                metadata,
                extra_data,
            };

            diesel::insert_into(flow::table)
                .values(&new_flow)
                .on_conflict_do_nothing()
                .execute(conn)
        },
        "alert" => {
            let new_alert = NewAlert {
                flow_id,
                timestamp,
                extra_data: eve_json.get("alert").cloned()
            };

            diesel::insert_into(alert::table)
                .values(&new_alert)
                .on_conflict_do_nothing()
                .execute(conn)
        },
        "anomaly" => {
            let new_anomaly = NewAnomaly {
                flow_id,
                timestamp,
                extra_data: eve_json.get("anomaly").cloned()
            };

            diesel::insert_into(anomaly::table)
                .values(&new_anomaly)
                .on_conflict_do_nothing()
                .execute(conn)
        },
        "fileinfo" => {
            let new_fileinfo = NewFileinfo {
                flow_id,
                timestamp,
                extra_data: eve_json.get("fileinfo").cloned()
            };

            diesel::insert_into(fileinfo::table)
                .values(&new_fileinfo)
                .on_conflict_do_nothing()
                .execute(conn)
        },
        _ => {
            let new_app_event = NewAppEvent {
                flow_id,
                timestamp,
                app_proto: event_type.to_string(),
                extra_data: eve_json.get(event_type).cloned()
            };

            diesel::insert_into(app_event::table)
                .values(&new_app_event)
                .on_conflict_do_nothing()
                .execute(conn)
        }
    }
}

pub struct Database {
    conn: PgConnection,
    rx: std::sync::mpsc::Receiver<String>,
    count: usize,
    count_inserted: usize,
}

impl Database {
    /// Open Postgres database connection.
    pub fn new(
        url: String,
        rx: std::sync::mpsc::Receiver<String>,
    ) -> Result<Self, ConnectionError> {
        let mut conn = PgConnection::establish(&url)?;
        conn.run_pending_migrations(MIGRATIONS).unwrap();

        Ok(Self {
            conn,
            rx,
            count: 0,
            count_inserted: 0,
        })
    }

    fn batch_write_events(&mut self) -> Result<(), diesel::result::Error> {
        while let Ok(buf) = self.rx.recv() {
            // Insert first event
            self.count += 1;
            self.count_inserted += write_event(&mut self.conn, &buf)?;

            // Insert remaining events
            let batch = self
                .rx
                .try_iter()
                .map(|buf| write_event(&mut self.conn, &buf))
                .collect::<Result<Vec<_>, _>>()?;
            self.count += batch.len();
            self.count_inserted += batch.iter().sum::<usize>();
        }
        Ok(())
    }

    /// Database thread entry
    pub fn run(&mut self) {
        log::debug!("Database thread started");
        if let Err(err) = self.batch_write_events() {
            log::error!("Failed to write batch of events: {err:?}");
        }
        log::info!(
            "Database thread finished: count={} inserted={}",
            self.count,
            self.count_inserted
        );
    }
}
