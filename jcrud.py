import json
import os.path
from typing import Optional

file_name = 'dbs/config.json'


def read_token() -> Optional[str]:
    val = read_value('TOKEN')
    return None if type(val) is not str else val


def read_description() -> Optional[str]:
    val = read_value('DESCRIPTION')
    return None if type(val) is not str else val


def read_about() -> Optional[str]:
    val = read_value('ABOUT')
    return None if type(val) is not str else val


def write_value(key: str, val) -> Optional[bool]:
    if not os.path.isfile(file_name):
        return None

    try:
        data = None
        res = False

        with open(file_name, 'r') as rf:
            data = json.load(rf)
            res = key in dict(data).keys()

        with open(file_name, 'w') as wf:
            data[key] = val
            json.dump(data, wf)
            return res

    except Exception as e:
        print('write_value: ' + str(e))
        return None


def read_value(key: str):
    if not os.path.isfile(file_name):
        return None

    try:
        data = {}
        res = False

        with open(file_name, 'r') as rf:
            data = json.load(rf)
            if key not in dict(data).keys():
                return None
            else:
                return data[key]

    except Exception as e:
        print('read_value: ' + str(e))
        return None

