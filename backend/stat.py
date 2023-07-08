import json
import platform
import threading

import requests

from events import events
from version import version


def get_mac():
    import uuid
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    mac_address = '-'.join([mac_address[i:i + 2] for i in range(0, 11, 2)])
    return mac_address


def check_newest():
    t = threading.Thread(target=do_check_newest)
    t.start()


def do_check_newest():
    data = {
        "app": {
            "name": "Copybook",
            "version": version["curr"],
            "md5sum": "",
            "statistics": {}
        },
        "host": {
            "os": platform.platform(),
            "mac": get_mac(),
            "ext": {
                "uname": platform.uname(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
            }
        }
    }

    try:
        response = requests.post("http://home.mydata.top:8681/api/copybook/check_newest", data=json.dumps(data))
        print(threading.currentThread().getName(), "check_newest: ", response.text)
        res = response.json()
        if res["result"]["code"] != 0 or "new_version" not in res:
            return
        new_version = res["info"]
        events.signal_check_newest.emit(new_version)
    except:
        return
