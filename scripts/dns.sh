#!/bin/bash

if [[ -z $1 ]]; then
    echo "Input .pcap file not provided"
    exit 1
fi

tcpdump -r "$1" -n -tttt  | perl -ne 'print if /A\?/'
