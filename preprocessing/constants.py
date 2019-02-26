#!/usr/bin/env python3

from enum import Enum
import os
import threading
import json


class Test(Enum):

    TEST_DATA_FOLDER = "/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4"
    DELETED_TEST_DATA_FOLDER = "/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/deleted"


JSON_FILE_PATH = os.path.abspath("../data/mxl_info.json")

json_lock = threading.Lock()
json_dict = {"count": 0}
try:
    with open(JSON_FILE_PATH, 'r') as fp:
        json_dict = json.load(fp)
        json_dict["count"] = 0
except:
    pass
