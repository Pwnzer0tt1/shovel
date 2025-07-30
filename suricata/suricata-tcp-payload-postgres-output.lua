-- Copyright (C) 2024  ANSSI
-- SPDX-License-Identifier: GPL-2.0-or-later

-- This Suricata plugin logs TCP flows data to a PostgreSQL database.

function init (args)
    local needs = {}
    needs["type"] = "streaming"
    needs["filter"] = "tcp"
    return needs
end

function setup (args)
    SCLogNotice("Initializing plugin TCP payload PostgreSQL Output; author=ANSSI; license=GPL-2.0")

    -- Open database connection
    luasql = require("luasql.postgres")
    env = assert(luasql.postgres())
    con = assert(env:connect("postgres", "postgres", "", "postgres"))

    -- packer counter for each flow
    flow_pkt_count = {}
    flow_pkt_count_total = 0
end

function log (args)
    -- create log entry
    local flow_id = SCFlowId()
    if flow_pkt_count[flow_id] == nil then
        flow_pkt_count[flow_id] = 0
    else
        flow_pkt_count[flow_id] = flow_pkt_count[flow_id] + 1
    end
    local count = flow_pkt_count[flow_id]
    flow_pkt_count_total = flow_pkt_count_total + 1
    local data, sb_open, sb_close, sb_ts, sb_tc = SCStreamingBuffer()
    if #data == 0 then
        return
    end
    local direction = "0"
    if sb_tc then
        direction = "1"
    end

    assert(con:execute(string.format([[INSERT INTO raw (flow_id, count, server_to_client, blob) VALUES (%s, %s, %s, '%s'::bytea) ON CONFLICT (id) DO NOTHING;]], flow_id, count, direction, data)))
end

function deinit (args)
    SCLogNotice("TCP payloads logged: " .. flow_pkt_count_total)
    database:close()
end
