#!/usr/bin/env python3

import json
import os
import threading
import traceback

_SETTINGS_LOCATION = os.path.abspath("../data/.settings.json")

settings_dict = None

try:
    with open(_SETTINGS_LOCATION, 'r') as fp:
        settings_dict = json.load(fp)
except FileNotFoundError:
    pass

if not settings_dict:
    settings_dict = {
        "locations": {
            "TEST_DATA_FOLDER": os.path.abspath("../data/MXL/TestData"),
            "DELETED_TEST_DATA_FOLDER": os.path.abspath("../data/MXL/deleted"),
            "JSON_FILE_PATH": os.path.abspath("../data/mxl_info.json")
        },
        "updates": {
            "FORCE": True,
            "UPDATE": True
        },
        "preprocessing": {
            "MIN_PITCH": 49.0,
            "MAX_PITCH": 84.0,
            "DELETE_PART_THRESHOLD": 0.65,
            "DELETE_STREAM_THRESHOLD": 0.8,
            "ACCEPTED_KEY": "C major"
        }
    }

    try:
        with open(_SETTINGS_LOCATION, 'x') as fp:
            fp.write(json.dumps(settings_dict, indent=2))
    except:
        traceback.print_exc()

TEST_DATA_FOLDER = settings_dict["locations"]["TEST_DATA_FOLDER"]
DELETED_TEST_DATA_FOLDER = settings_dict["locations"]["DELETED_TEST_DATA_FOLDER"]

JSON_FILE_PATH = settings_dict["locations"]["JSON_FILE_PATH"]

FORCE = settings_dict["updates"]["FORCE"]
UPDATE = settings_dict["updates"]["UPDATE"]

PREP_SETTINGS = settings_dict["preprocessing"]

json_lock = threading.Lock()

try:
    with open(JSON_FILE_PATH, 'r') as fp:
        json_dict = json.load(fp)
        json_dict["count"] = 0
except FileNotFoundError:
    json_dict = {"count": 0}
