#!/usr/bin/python
"""
bulkhover.py 1.1

This is a command-line script to import and export DNS records for a single
domain into or out of a hover account.

Usage:
  bulkhover.py [options] (import|export) <domain> <dnsfile>
  bulkhover.py (-h | --help)
  bulkhover.py --version

Options:
  -h --help             Show this screen
  --version             Show version
  -c --conf=<conf>      Path to conf
  -u --username=<user>  Your hover username
  -p --password=<pass>  Your hover password
  -f --flush            Delete all existing records before importing

Examples:
  The DNS file should have one record per line, in the format:
  {name} {type} {content}

  For example:

  www A 127.0.0.1
  @ MX 10 example.com

  
  Since the script output is in the same format as its input, you can copy the
  entire contents of one domain to another, like so:

  bulkhover.py -c my.conf export example.com - | ./bulkhover.py -c my.conf -f import other.com -


  To avoid passing your username and password in the command-line, you can use
  a conf file that contains them instead:

  [hover]
  username=YOUR_USERNAME
  password=YOUR_PASSWORD
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


def import_dns(username, password, domain, filename, flush=False):
    try:
        client = HoverAPI(username, password)
    except HoverException as e:
        raise HoverException("Authentication failed")
    if flush:
        records = client.call("get", "domains/{0}/dns".format(domain))["domains"][0]["entries"]
        for record in records:
            client.call("delete", "dns/{0}".format(record["id"]))
            print "Deleted {name} {type} {content}".format(**record)
    
    domain_id = client.call("get", "domains/{0}".format(domain))["domain"]["id"]
    
    if filename == "-": filename = "/dev/stdin"
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split(" ", 2)
            record = {"name": parts[0], "type": parts[1], "content": parts[2]}
            client.call("post", "domains/{0}/dns".format(domain), record)
            print "Created {name} {type} {content}".format(**record)


def export_dns(username, password, domain, filename):
    try:
        client = HoverAPI(username, password)
    except HoverException as e:
        raise HoverException("Authentication failed")
    records = client.call("get", "domains/{0}/dns".format(domain))["domains"][0]["entries"]
    
    if filename == "-": filename = "/dev/stdout"
    with open(filename, "w") as f:
        for record in records:
            f.write("{name} {type} {content}\n".format(**record))
    

def main(args):
    def get_conf(filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        items = dict(config.items("hover"))
        return items["username"], items["password"]

    if args["--conf"] is None:
        if not all((args["--username"], args["--password"])):
            print("You must specifiy either a conf file, or a username and password")
            return 1
        else:
            username, password = args["--username"], args["--password"]
    else:
        username, password = get_conf(args["--conf"])

    try:
        if args["import"]:
            import_dns(username, password, args["<domain>"], args["<dnsfile>"], args["--flush"])
        elif args["export"]:
            export_dns(username, password, args["<domain>"], args["<dnsfile>"])
    except HoverException as e:
        print "Unable to update DNS: {0}".format(e)
        return 1


if __name__ == "__main__":
    version = __doc__.strip().split("\n")[0]
    args = docopt.docopt(__doc__, version=version)
    status = main(args)
    sys.exit(status)
