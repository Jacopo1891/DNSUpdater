import os, sys, requests
from lexicon.client import Client
from lexicon.config import ConfigResolver
from config import *

DEBUG = "--debug" in sys.argv

def check_config():
    if record_url == "":
        print("Record url is empty: cannot start.")
        sys.exit(1)
    if lexicon_config == {}:
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
    url = "https://ifconfig.me/"
    return requests.get(url).text.strip()

def get_vpn_ip_address(config):
    with Client(config) as operations:
        records = operations.list_records(name=record_url)
        if records and len(records) > 0:
            return records[0]["content"]
    return None

def update_record_vpn(config, current_ip_address):
    with Client(config) as operations:
        return operations.update_record(name=record_url, content=current_ip_address)

def create_record_vpn(config, current_ip_address):
    with Client(config) as operations:
        return operations.create_record(rtype="A", name=record_url, content=current_ip_address)

def send_notification(current_ip_address, result):
    if bot_token is not None and chat_id is not None:
        return send_telegram_message(current_ip_address)
    return result

def send_telegram_message(current_ip_address):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": f"Server has a new ip: {current_ip_address}."
    }
    response = requests.post(url, json=params)
    return response.status_code == 200

def main():
    check_config()
    config_resolver = ConfigResolver().with_dict(lexicon_config)

    current_ip_address = get_current_ip_address()
    record_ip_address = get_vpn_ip_address(config_resolver)

    if current_ip_address is None:
        print("Current ip is not valid.")
        sys.exit(1)       
    if record_ip_address is None:
        result = create_record_vpn(config_resolver, current_ip_address)
    elif record_ip_address != current_ip_address:
        result = update_record_vpn(config_resolver, current_ip_address)
    else:
        result = None

    if result:
        result = send_notification(current_ip_address, result)

    if DEBUG:
        print_debug_info(current_ip_address, record_ip_address, result)

if __name__ == "__main__":
    main()