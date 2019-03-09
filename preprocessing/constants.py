#!/usr/bin/env python3

import json
import os
import threading
import traceback

os.chdir("/home/malte/PycharmProjects/BachelorMusic")

__SETTINGS_LOCATION = os.path.abspath("data/.settings.json")

settings_dict = None

try:
    with open(__SETTINGS_LOCATION, 'r') as fp:
        settings_dict = json.load(fp)
except FileNotFoundError:
    pass

if not settings_dict:
    settings_dict = {
        "locations": {
            "TEST_DATA_FOLDER": os.path.abspath("data/MXL/TestData"),
            "DELETED_TEST_DATA_FOLDER": os.path.abspath("data/MXL/deleted"),
            "JSON_FILE_PATH": os.path.abspath("data/mxl_info.json"),
            "MELODY_INFORMATION": os.path.abspath("data/melody_info.json")
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
            "ACCEPTED_KEY": "C major",
            "MAX_BPM": 140,
            "MIN_BPM": 100,
            "VALID_TIME": "4/4"
        }
    }

    try:
        with open(__SETTINGS_LOCATION, 'x') as fp:
            fp.write(json.dumps(settings_dict, indent=2))
    except:
        traceback.print_exc()

TEST_DATA_FOLDER = settings_dict["locations"]["TEST_DATA_FOLDER"]
DELETED_TEST_DATA_FOLDER = settings_dict["locations"]["DELETED_TEST_DATA_FOLDER"]

JSON_FILE_PATH = settings_dict["locations"]["JSON_FILE_PATH"]
MELODY_FILE_PATH = settings_dict["locations"]["MELODY_INFORMATION"]

FORCE = settings_dict["updates"]["FORCE"]
UPDATE = settings_dict["updates"]["UPDATE"]

PREP_SETTINGS = settings_dict["preprocessing"]

json_lock = threading.Lock()
melody_lock = threading.Lock()

try:
    with open(JSON_FILE_PATH, 'r') as fp:
        json_dict = json.load(fp)
        json_dict["count"] = 0
except FileNotFoundError:
    json_dict = {"count": 0}


def make_chord_dict() -> dict:
    import music21 as m21

    maj = m21.chord.Chord(['C', 'E', 'G'])
    min = m21.chord.Chord(['C', 'E-', 'G'])
    dim = m21.chord.Chord(['C', 'E-', 'G-'])
    maj7 = m21.chord.Chord(['C', 'E', 'G', 'B'])
    min7 = m21.chord.Chord(['C', 'E-', 'G', 'B-'])

    base_note = m21.note.Note('C')

    chord_dict = {}

    for _ in range(12):
        chord_dict[base_note.name + " major"] = [p.ps % 12 for p in maj.pitches]
        maj = maj.transpose(1)
        chord_dict[base_note.name + " minor"] = [p.ps % 12 for p in min.pitches]
        min = min.transpose(1)
        chord_dict[base_note.name + " diminished"] = [p.ps % 12 for p in dim.pitches]
        dim = dim.transpose(1)
        chord_dict[base_note.name + " major 7"] = [p.ps % 12 for p in maj7.pitches]
        maj7 = maj7.transpose(1)
        chord_dict[base_note.name + " minor 7"] = [p.ps % 12 for p in min7.pitches]
        min7 = min7.transpose(1)

        base_note = base_note.transpose(1)

    note_dict = {}
    for i in range(12):
        note_dict[str(i)] = []

    for key in chord_dict:
        for pitch in chord_dict[key]:
            note_dict[str(int(pitch))].append(key)

    full_dict = {
        "note_to_chords": note_dict,
        "chord_to_notes": chord_dict
    }

    with open(__CHORD_DATA_LOCATION, 'x') as fp:
        fp.write(json.dumps(full_dict, indent=2))

    return full_dict


__CHORD_DATA_LOCATION = os.path.abspath("data/chord_data.json")
try:
    with open(__CHORD_DATA_LOCATION, 'r') as fp:
        chord_data = json.load(fp)
except FileNotFoundError:
    chord_data = make_chord_dict()
