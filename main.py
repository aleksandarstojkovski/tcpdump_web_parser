from flask import Flask, render_template
import re

from DNSTableEntry import DNSTableEntry
from WebsiteEntry import WebsiteEntry
from HTTPSTableEntry import HTTPSTableEntry
import os
import sys
import subprocess

app = Flask(__name__)

http_output_file_name = "http.txt"
tcpdump_pcap_file = "tcpdump.pcap"

open(http_output_file_name, 'w').close()
httpRegex = re.compile(r'(^\S+?)\s+?(\S+?)\s+?(\S+?)\s+?(\S+?)\s.*?(GET)\s+?(\S+?)\s+?(\S+?)\s+')
http_log = subprocess.Popen(["httpry", "-o", http_output_file_name])

dnsRegex = re.compile(r'(\S+)\s(\S+)\s\S+\s(\S+)\s\S+\s(\S+)\s\S+\s\S+\s\S+\s(\S+)')
tcpdump = subprocess.Popen(["tcpdump", "-i", "any", "-w", tcpdump_pcap_file])


def read_http_file() -> list:
    table_entries = []
    http_output_file = open(http_output_file_name, 'r')
    for line in http_output_file.readlines():
        match = httpRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, method, website, path = match.groups()
            table_entries.append(WebsiteEntry(date, time, ip_src, ip_dst, method, website, path))
    return table_entries


def read_dns_file() -> list:
    table_entries = []
    dns_entries = subprocess.Popen([os.getcwd() + "/dns.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, website = match.groups()
            website = website[:-1]
            ip_dst = ip_dst[:-1]
            table_entries.append(DNSTableEntry(date, time, ip_src, ip_dst, website))
    return table_entries


def read_https_file() -> list:
    table_entries = []
    dns_entries = subprocess.Popen([os.getcwd() + "/https.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, oth = match.groups()
            table_entries.append(HTTPSTableEntry(date, time, ip_src, ip_dst))
    return table_entries


def read_dns_uniq_file() -> list:
    table_entries = []
    dns_entries = subprocess.Popen([os.getcwd() + "/dns.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, website = match.groups()
            website = website[:-1]
            table_entries.append(website)
    return list(set(table_entries))


@app.route('/http')
def http():
    return render_template('http.html', my_list=read_http_file())


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/dns')
def dns():
    return render_template('dns.html', my_list=read_dns_file())


@app.route('/https')
def https():
    return render_template('https.html', my_list=read_https_file())


@app.route('/dns-uniq')
def dns_uniq():
    return render_template('dns-uniq.html', my_list=read_dns_uniq_file())
