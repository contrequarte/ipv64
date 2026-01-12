
# https://github.com/contrequarte/ipv64#

import requests
import json
from datetime import datetime

BEARER_VALUE = 'invalid'
DOMAIN_TOKEN = 'invalid'
DOMAIN = 'invalid'

#sample for cron scheduling to execute the update check each 5 mins
#                folder of the py script    python interpreter script name       log file location
# */5 * * * * cd /home/ubuntu/ipv64update/; /usr/bin/python3 ./ipv64update.py >> /var/log/ipv64updates.log 2>&1

def load_configured_values():
    #
    # The content of the config file "config.json" should look as follows:
    # {
    #     "bearer_value": "your bearer value here",
    #     "domain": "your ipv64 dyndns domain here",
    #     "domain_token": "your domain token here"
    # }
    #
    with open('./config.json', 'r') as c:
        config = json.load(c)

    global BEARER_VALUE, DOMAIN_TOKEN, DOMAIN
    BEARER_VALUE = config["bearer_value"]
    DOMAIN_TOKEN = config["domain_token"]
    DOMAIN = config["domain"]

def get_current_ip():
    resp = requests.get('https://checkip.amazonaws.com')
    if resp.status_code == 200:
        return resp.text.replace('\n', '')
    else:
        return "unknown"


def get_ip_configured():
    headers = {
        'Authorization': f"Bearer {BEARER_VALUE}",
    }
    response = requests.get('https://ipv64.net/api.php?get_domains', headers=headers)
    if response.status_code == 200:
        return response.json()['subdomains'][DOMAIN]['records'][0]['content']
    else:
        return "unknown"


def set_current_ip(domain_token, domain, ip):
    params = {
        'key': domain_token,
        'domain': domain,
        'ip': ip,
    }

    response = requests.get('https://ipv64.net/nic/update', params=params)
    print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} {response} ---> {response.text}")
    if response.status_code == 200:
        return True
    else:
        return False


def main():
    load_configured_values()
    ip_configured = get_ip_configured()
    ip_current = get_current_ip()
    print(
        f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} current: {ip_current} <---> currently configured: {ip_configured}")
    if ip_current != 'unknown' and ip_configured != 'unknown':
        if ip_current != ip_configured:
            #update required
            if set_current_ip(DOMAIN_TOKEN, DOMAIN, ip_current):
                print(
                    f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} Successfully updated IP address to: {ip_current}! ")
        else:
            #nothing to do
            print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} NO IP address update required!")


main()
