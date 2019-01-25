#!/usr/bin/python3

from urllib.request import urlopen
from netaddr import IPAddress, IPNetwork
import ssl
import re
import sys
import getopt
import urllib
import ipaddress


def main(argv):

    # parse ip from input
    if len(argv) == 0:
        usage()
        sys.exit(2)
    try:
        ip_address = get_ip_address(argv)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    # fetch logs from url
    logs_url = "https://s3.amazonaws.com/syseng-challenge/public_access.log.txt"
    try:
        logs_list = fetch_logs(logs_url)
        # print(len(logs_list))
    except urllib.error.URLError as err:
        print("Error while reading logs from the bucket..")
        print(str(err))
        sys.exit(1)

    count = 0
    # Print logs for an IP
    if re.search("/", ip_address) is None:
        for log in logs_list:
            if re.search(ip_address, log) is not None:
                count += 1
                print(log)
    # Print logs for an IP CIDR network
    else:
        for log in logs_list:
            ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', log)
            if ip:
                # print(ip)
                try:
                    if IPAddress(ip[0]) in IPNetwork(ip_address):
                        count += 1
                        print(log)
                except Exception as err:
                    print("Error occurred while validating CIDR range..")
                    print(str(err))
                    sys.exit(2)
    # print(count)


def fetch_logs(logs_url):
    context = ssl._create_unverified_context()
    response = urlopen(logs_url, context=context)
    # print("Fetching logs..")
    data = response.read()
    text = data.decode("utf-8")

    return text.split("\n")


def get_ip_address(argv):
    opts, args = getopt.getopt(argv, "", ["ip="])
    for opt in opts:
        key = opt[0]
        if key == "--ip":
            ip_address = opt[1]
            # print(ip_address)
            try:
                ipaddress.ip_network(ip_address)
                return ip_address
            except ValueError as err:
                print("Invalid input..")
                print(str(err))
                sys.exit(2)

def usage():
    print("Invalid input..")
    print("Command: python3 weblog_helper.py --ip <ip_address/ip_network>")

if __name__ == "__main__":
   main(sys.argv[1:])
