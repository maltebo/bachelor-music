#!/usr/bin/env python3

# sets up constants: in functions, so that we can handle data that's not on the working laptop

import os
import sys
import time

# sets directory and adds path so that relative imports work
project_folder = os.path.abspath(os.path.dirname(__file__)).split('/settings')[0]
os.chdir(project_folder)
sys.path.append(project_folder)

print("start variable setup")
start_time = time.time()

# constants for folder locations
MXL_DATA_FOLDER = os.path.join(project_folder, "data/MXL/lmd_matched_mxl")
MUSIC_INFO_FOLDER_PATH = os.path.join(project_folder, "data/music_info_pb")
MELODY_FILE_PATH = os.path.join(project_folder, "data/melody_files/melody_info.json")
DELETED_PIECES_PATH = os.path.join(project_folder, "data/MXL/deleted_pieces")

print("finished setup in {sec} seconds".format(sec=str(round(time.time() - start_time, 2))))
