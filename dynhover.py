#!/usr/bin/env python
"""
dynhover.py 1.1

Usage:
  dynhover.py (-c <conf> | -u <user> -p <password>) <domain>
  dynhover.py (-h | --help)
  dynhover.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  -c --conf=<conf>      Path to conf.
  -u --username=<user>  Your hover username.
  -p --password=<pass>  Your hover password.
"""

import ConfigParser
import docopt
import requests
import sys


class HoverException(Exception):
    pass


class HoverAPI(object):
    def __init__(self, username, password):
        params = {"username": username, "password": password}
        r = requests.post("https://www.hover.com/api/login", params=params)
        if not r.ok or "hoverauth" not in r.cookies:
            raise HoverException(r)
        self.cookies = {"hoverauth": r.cookies["hoverauth"]}
    def call(self, method, resource, data=None):
        url = "https://www.hover.com/api/{0}".format(resource)
        r = requests.request(method, url, data=data, cookies=self.cookies)
        if not r.ok:
            raise HoverException(r)
        if r.content:
            body = r.json()
            if "succeeded" not in body or body["succeeded"] is not True:
                raise HoverException(body)
            return body


def get_public_ip():
    return requests.get("http://ifconfig.me/ip").content


def update_dns(username, password, fqdn):
    try:
        client = HoverAPI(username, password)
    except HoverException as e:
        raise HoverException("Authentication failed")
    dns = client.call("get", "dns")
    dns_id = None
    for domain in dns["domains"]:
        if fqdn == domain["domain_name"]:
            fqdn = "@.{domain_name}".format(**domain)
        for entry in domain["entries"]:
            if entry["type"] != "A": continue
            if "{0}.{1}".format(entry["name"], domain["domain_name"]) == fqdn:
                dns_id = entry["id"]
                break
    if dns_id is None:
        raise HoverException("No DNS record found for {0}".format(fqdn))

    my_ip = get_public_ip()

    response = client.call("put", "dns/{0}".format(dns_id), {"content": my_ip})
    
    if "succeeded" not in response or response["succeeded"] is not True:
        raise HoverException(response)
    

def main(args):
    if args["--username"]:
        username, password = args["--username"], args["--password"]
    else:
        config = ConfigParser.ConfigParser()
        config.read(args["--conf"])
        items = dict(config.items("hover"))
        username, password = items["username"], items["password"]

    domain = args["<domain>"]
    
    try:
        update_dns(username, password, domain)
    except HoverException as e:
        print "Unable to update DNS: {0}".format(e)
        return 1
    
    return 0


if __name__ == "__main__":
    version = __doc__.strip().split("\n")[0]
    args = docopt.docopt(__doc__, version=version)
    status = main(args)
    sys.exit(status)
