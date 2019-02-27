import preprocessing.constants as c
from statistics import mean
from preprocessing.vanilla_stream import VanillaStream
import traceback
from copy import deepcopy
import json


def make_stream_dict(m21_stream: VanillaStream):
    stream_info = {"metronome_range": (m21_stream.metronome_mark_min, m21_stream.metronome_mark_max),
                   "time_signature": m21_stream.time_signature}
    stream_key = m21_stream.analyze('key')
    stream_info["key_and_correlation"] = (stream_key.name, stream_key.correlationCoefficient)
    parts_info = {}
    number = 2
    for p in m21_stream.parts:
        part_info = {"average_pitch": mean(p.pitch_list), "average_volume": mean(p.volume_list)}
        part_key = p.analyze('key')

        if stream_key.name != part_key.name:
            for k in part_key.alternateInterpretations:
                if k.name == stream_key.name:
                    part_key = k
                    break

        if stream_key.name != part_key.name:
            part_key = deepcopy(stream_key)
            part_key.correlationCoefficient = -1.0

        assert stream_key.name == part_key.name

        part_info["key_and_correlation"] = (part_key.name, part_key.correlationCoefficient)
        if p.total_notes_or_chords:
            part_info["note_percentage"] = p.note_number / p.total_notes_or_chords
            part_info["lyrics_percentage"] = p.lyrics_number / p.total_notes_or_chords
        else:
            part_info["note_percentage"] = 0.0
            part_info["lyrics_percentage"] = 0.0
        if p.partName in parts_info:
            parts_info[p.partName + "_" + str(number)] = part_info
            number += 1
        else:
            parts_info[p.partName] = part_info

    stream_info["parts"] = parts_info

    return stream_info


def put_in_json_dict(dict_id: str, stream_info: dict, force: bool = False):
    c.json_lock.acquire()
    try:
        if not force and valid_entry_exists(dict_id):
            c.json_lock.release()
            return
        c.json_dict["count"] += 1

        c.json_dict[dict_id] = stream_info

        if c.json_dict["count"] >= 5:
            print("write json dict")
            with open(c.JSON_FILE_PATH, 'w') as fp:
                fp.write(json.dumps(c.json_dict, indent=2))
            c.json_dict["count"] = 0
        c.json_lock.release()
    except:
        traceback.print_exc()
        c.json_lock.release()


def valid_entry_exists(id: str) -> bool:
    if not id in c.json_dict:
        return False

    stream_dict = c.json_dict[id]
    if not ("metronome_range" in stream_dict and "time_signature" in stream_dict and
            "key_and_correlation" in stream_dict and "parts" in stream_dict):
        return False

    for part_dict in stream_dict["parts"]:
        if not _is_valid_part_entry(stream_dict["parts"][part_dict], stream_dict["key_and_correlation"]):
            return False

    return True


def _is_valid_part_entry(part_dict: dict, key_and_correlation: tuple):
    if not ("average_pitch" in part_dict and "average_volume" in part_dict and
            "key_and_correlation" in part_dict and "note_percentage" in part_dict and
            "lyrics_percentage" in part_dict):
        return False

    if part_dict["key_and_correlation"][0] != key_and_correlation[0]:
        return False

    return True
