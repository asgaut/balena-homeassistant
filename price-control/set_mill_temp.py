import json
import os
import sys
import urllib.request

def set_mill_temp(mill_ip, temperature: float, verbose: bool):

    if temperature < 5 or temperature > 35:
        raise ValueError("Temperature must be between 5 and 35")

    url = "http://" + mill_ip + "/set-temperature"
    data = {
        "type": "Normal",
        "value": temperature
    }
    headers = {
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers)
    with urllib.request.urlopen(req) as f:
        if verbose:
            print("HTTP status code:", f.status)
            headers = f.getheaders()
            content_type = f.getheader('Content-Type')
            print("Content-Type:", content_type)
            if content_type == "application/json":
                print(json.loads(f.read()))
            else:
                print(f.read())

if __name__ ==  '__main__':
    mill_ip = os.environ.get("MILL_IP")

    if mill_ip == None:
        sys.stderr.write("MILL_IP environment variable must be set")
        sys.exit(1)

    temperature = float(sys.argv[1])

    set_mill_temp(mill_ip, temperature, True)
