-- Copyright (C) 2024  ANSSI
-- SPDX-License-Identifier: GPL-2.0-or-later

-- This Suricata plugin logs UDP frames data to a PostgreSQL database.

function init (args)
    local needs = {}
    needs["type"] = "packet"
    return needs
end

function setup (args)
    SCLogNotice("Initializing plugin UDP payload PostgreSQL Output; author=ANSSI; license=GPL-2.0")

    -- Open database connection
    pgmoon = require("pgmoon")
    pg = pgmoon.new({
        host = "postgres",
        port = "5432",
        database = "postgres",
        user = "postgres"
    })
    assert(pg:connect())

    -- packer counter for each flow
    flow_pkt_count = {}
    flow_pkt_count_total = 0
end

encode_bytea = function(str)
  return string.format("%s", str:gsub('.', function(byte)
    return string.format('%02x', string.byte(byte))
  end))
end

function log (args)
    -- drop if not UDP (17)
    -- https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    local ipver, srcip, dstip, proto, sp, dp = SCPacketTuple()
    if proto ~= 17 then
        return
    end

    -- get packet direction
    local ipver, srcip_flow, dstip_flow, proto, sp_flow, dp_flow = SCFlowTuple()
    local direction = 1
    if srcip == srcip_flow and dstip == dstip_flow and sp == sp_flow and dp == dp_flow then
        direction = 0
    end

    -- create log entry
    local flow_id = SCFlowId()
    if flow_pkt_count[flow_id] == nil then
        flow_pkt_count[flow_id] = 0
    else
        flow_pkt_count[flow_id] = flow_pkt_count[flow_id] + 1
    end
    local count = flow_pkt_count[flow_id]
    flow_pkt_count_total = flow_pkt_count_total + 1
    local data = SCPacketPayload()
    if #data == 0 then
        return
    end
    
    assert(pg:query("INSERT INTO raw (flow_id, count, server_to_client, blob) VALUES ($1, $2, $3, decode($4, 'hex')) ON CONFLICT (id) DO NOTHING;", flow_id, count, direction, encode_bytea(data)))
end

function deinit (args)
    SCLogNotice("UDP payloads logged: " .. flow_pkt_count_total)
    database:close()
end
