import os
import sys
from lexicon.client import Client
from lexicon.config import ConfigResolver
from lexicon.providers.ovh import Provider

from config import *

DEBUG = "--debug" in sys.argv

def check_config():
    if recordUrl == "":
        print("Record url is empty: cannot start.")
        sys.exit(1)
    if LexiconConfig == {}:
        print("Lexicon's config is empty: cannot start.")
        sys.exit(1)

def print_debug_info(current_ip_address, record_ip_address, result):
    print("Current public IP:", current_ip_address)
    print("Current record IP:", record_ip_address)
    if result:
        print("IP updated")
    elif result is None:
        print("IP is up to date")
    else:
        print("Something went wrong")

def get_current_ip_address():
    return os.popen('curl -s https://api.ipify.org').read().strip()

def get_vpn_ip_address(provider):
    record_ip_address_response = provider.list_records(name=recordUrl)
    if len(record_ip_address_response) > 0:
        return record_ip_address_response[0]["content"]
    return None

def update_record_vpn(provider, current_ip_address):
    return provider.update_record(name=recordUrl, content=current_ip_address)

def create_record_vpn(provider, current_ip_address):
    return provider.create_record(rtype="A", name=recordUrl, content=current_ip_address)

def main():
    check_config()
    provider = Provider(LexiconConfig)
    provider.authenticate()

    current_ip_address = get_current_ip_address()
    record_ip_address = get_vpn_ip_address(provider)

    if record_ip_address is None:
        result = create_record_vpn(provider, current_ip_address)
    elif record_ip_address != current_ip_address:
        result = update_record_vpn(provider, current_ip_address)
    else:
        result = None
        
    if DEBUG:
        print_debug_info(current_ip_address, record_ip_address, result)

if __name__ == "__main__":
    main()