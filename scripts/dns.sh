#!/bin/bash

if [[ -z $1 ]]; then
    echo "Input .pcap file not provided"
    exit 1
fi

tcpdump -r "$1" -n -tttt  | perl -lane 'print if $F[7]=~/\[1au\]/ and $F[8]=~/^A\?/'
