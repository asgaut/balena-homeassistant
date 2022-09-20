import datetime
import json
import os
import sys
import urllib.request

def print_status(mill_ip):
    with urllib.request.urlopen("http://"+mill_ip+"/control-status") as url:
        data = json.loads(url.read().decode())
        print(datetime.datetime.now(), "mill status:", data)

if __name__ ==  '__main__':
    mill_ip = os.environ.get("MILL_IP")

    if mill_ip == None:
        sys.stderr.write("MILL_IP environment variable must be set")
        sys.exit(1)

    print_status(mill_ip)
