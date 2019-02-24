#!/usr/bin/env python3

from enum import Enum
import os

class Test(Enum):

    TEST_DATA_FOLDER = "/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4"
    DELETED_TEST_DATA_FOLDER = "/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/deleted"


class Info(Enum):
    time_sig = 1


JSON_FILE_PATH = os.path.abspath("../data/mxl_info.json")
