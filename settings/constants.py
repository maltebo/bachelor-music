#!/usr/bin/env python3

# sets up constants: in functions, so that we can handle data that's not on the working laptop

import os
import sys

# sets directory and adds path so that relative imports work
project_folder = os.path.abspath(os.path.dirname(__file__)).split('/settings')[0]
os.chdir(project_folder)
sys.path.append(project_folder)


# constants for folder locations
MXL_DATA_FOLDER = os.path.join(project_folder, "data/MXL/lmd_matched_mxl")
MUSIC_INFO_FOLDER_PATH = os.path.join(project_folder, "data/music_info_pb")
MELODY_FILE_PATH = os.path.join(project_folder, "data/melody_files/melody_info.json")
DELETED_PIECES_PATH = os.path.join(project_folder, "data/MXL/deleted_pieces")
PROTO_BUFFER_PATH = os.path.join(project_folder, "data/protobuffer")
TRANSFORMED_PROTO_BUFFER_PATH = os.path.join(project_folder, "data/protobuffer_data")
ALL_DATA = os.path.join(project_folder, "data/preprocessed_data")

os.makedirs(MXL_DATA_FOLDER, exist_ok=True)
os.makedirs(MUSIC_INFO_FOLDER_PATH, exist_ok=True)
os.makedirs(DELETED_PIECES_PATH, exist_ok=True)
os.makedirs(PROTO_BUFFER_PATH, exist_ok=True)
os.makedirs(TRANSFORMED_PROTO_BUFFER_PATH, exist_ok=True)
os.makedirs(ALL_DATA, exist_ok=True)

chord_to_idx = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "E#": 5,
    "Fb": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "B#": 0,
    "Cb": 11
}

idx_to_chord = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
