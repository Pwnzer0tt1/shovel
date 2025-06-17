#!/bin/bash

PCAP_BROKER_IP="$(dig +short ${PCAP_TCP_DOMAIN})"
PCAP_BROKER_PORT="${PCAP_TCP_PORT}"

touch "/dump-pcap/${PCAP_FILE_NAME}.pcap"

echo "Starting capturing $PCAP_BROKER_IP:$PCAP_BROKER_PORT on /dump-pcap/${PCAP_FILE_NAME}.pcap"

tshark -i "TCP@${PCAP_BROKER_IP}:${PCAP_BROKER_PORT}" -w "/dump-pcap/${PCAP_FILE_NAME}.pcap"