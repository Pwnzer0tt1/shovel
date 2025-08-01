use diesel::prelude::*;

use crate::schema::{alert, anomaly, app_event, fileinfo, flow};


#[derive(Insertable)]
#[diesel(table_name = flow)]
pub struct NewFlow<'a> {
    pub id: i64,
    pub src_ip: &'a str,
    pub src_port: Option<i32>,
    pub dest_ip: &'a str,
    pub dest_port: Option<i32>,
    pub pcap_filename: Option<&'a str>,
    pub proto: &'a str,
    pub app_proto: Option<&'a str>,
    pub metadata: Option<serde_json::Value>,
    pub extra_data: Option<serde_json::Value>
}

#[derive(Insertable)]
#[diesel(table_name = alert)]
pub struct NewAlert {
    pub flow_id: i64,
    pub timestamp: i64,
    pub extra_data: Option<serde_json::Value>
}

#[derive(Insertable)]
#[diesel(table_name = anomaly)]
pub struct NewAnomaly {
    pub flow_id: i64,
    pub timestamp: i64,
    pub extra_data: Option<serde_json::Value>
}

#[derive(Insertable)]
#[diesel(table_name = fileinfo)]
pub struct NewFileinfo {
    pub flow_id: i64,
    pub timestamp: i64,
    pub extra_data: Option<serde_json::Value>
}

#[derive(Insertable)]
#[diesel(table_name = app_event)]
pub struct NewAppEvent {
    pub flow_id: i64,
    pub timestamp: i64,
    pub app_proto: String,
    pub extra_data: Option<serde_json::Value>
}