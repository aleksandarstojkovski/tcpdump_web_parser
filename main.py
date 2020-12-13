from flask import Flask, render_template
from DNSTableEntry import DNSTableEntry
from WebsiteEntry import WebsiteEntry
from HTTPSTableEntry import HTTPSTableEntry
import re
import os
import sys
import argparse
import subprocess


app = Flask(__name__)


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
    dns_entries = subprocess.Popen([os.getcwd() + "scripts/dns.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, website = match.groups()
            website = website[:-1]
            ip_dst = ip_dst[:-4]
            table_entries.append(DNSTableEntry(date, time, ip_src, ip_dst, website))
    return table_entries


def read_https_file() -> list:
    table_entries = []
    dns_entries = subprocess.Popen([os.getcwd() + "scripts/https.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, oth = match.groups()
            ip_dst = ip_dst[:-5]
            table_entries.append(HTTPSTableEntry(date, time, ip_src, ip_dst))
    return table_entries


def read_dns_uniq_file() -> list:
    table_entries = []
    dns_entries = subprocess.Popen([os.getcwd() + "scripts/dns.sh", tcpdump_pcap_file], stdout=subprocess.PIPE,
                                   universal_newlines=True)
    stdout, stderr = dns_entries.communicate()
    for line in stdout.splitlines():
        match = dnsRegex.search(line)
        if match is not None:
            date, time, ip_src, ip_dst, website = match.groups()
            website = website[:-1]
            table_entries.append(website)
    return list(set(table_entries))


def check_prerequisites():
    prerequisites = ["tcpdump", "httpry"]
    for prerequisite in prerequisites:
        devnull = open(os.devnull, "w")
        return_val = subprocess.call(["which", prerequisite], stdout=devnull, stderr=devnull)
        devnull.close()
        if return_val != 0:
            print("Package {} not installed!".format(prerequisite))
            os._exit(1)
            sys.exit(1)


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser("TCPDump Web Parser")
    parser.add_argument("-s", type=str, help="Server (eg. 0.0.0.0), default 0.0.0.0", dest='server', default="0.0.0.0")
    parser.add_argument("-p", type=str, help="Port (eg. 80), default 80", dest='port', default="80")
    parser.add_argument("-i", type=str, help="Interface (eg. eth0), default any", dest='interface', default="any")
    parser.add_argument("-es", type=int, help="Exclude SSH (0 or 1), default 0", dest='excludeSSH', default=0)
    parser.add_argument("-rt", type=int, help="Regex type (0 or 1), default 0", dest='regexType', default=0)

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        os._exit(1)
        sys.exit(1)

    check_prerequisites()

    http_output_file_name = "http.txt"
    tcpdump_pcap_file = "tcpdump.pcap"

    if args.excludeSSH == 0:
        tcpdump_command = ["tcpdump", "-i", args.interface, "-w", tcpdump_pcap_file]
    else:
        tcpdump_command = ["tcpdump", "-i", "any", "-w", tcpdump_pcap_file, "not", "port", "22"]

    if args.regexType == 0:
        dnsRegex = re.compile(r'(\S+)\s(\S+)\s\S+\s(\S+)\s\S+\s(\S+)\s\S+\s\S+\s\S+\s(\S+)')
    else:
        dnsRegex = re.compile(r'(\S+)\s(\S+)\s\S+\s(\S+)\s\S+\s(\S+)\s\S+\s\S+\s(\S+)\s\S+')

    http_command = ["httpry", "-o", http_output_file_name]
    open(http_output_file_name, 'w').close()
    open(tcpdump_pcap_file, 'w').close()
    httpRegex = re.compile(r'(^\S+?)\s+?(\S+?)\s+?(\S+?)\s+?(\S+?)\s.*?(GET)\s+?(\S+?)\s+?(\S+?)\s+')

    http_log = subprocess.Popen(http_command)
    tcpdump = subprocess.Popen(tcpdump_command)

    app.run(port=args.port, host=args.server)

