#!/usr/bin/env python3

from music21 import *
import sys
import os
sys.path.append(os.path.abspath(".."))
from preprocessing.constants import *
from preprocessing.vanilla_stream import VanillaStream
from preprocessing.create_modified_stream import process_data
from preprocessing.find_melody import simple_skyline_algorithm
import threading
import queue
import time
import json
from statistics import mean, median, mode


def get_job(temp_queue):
    queue_lock.acquire()
    if not work_queue.empty():
        file_name = temp_queue.get()
        queue_lock.release()
        return file_name

    else:
        queue_lock.release()
        time.sleep(1)
        return None


def run_all(thread_nr):
    while not work_queue.empty():
        force_dict = True
        # Todo change value
        file_name = get_job(work_queue)
        if not file_name:
            continue
        if not force_dict and file_name in json_dict:
            continue
        m21_stream = process_data(thread_nr, file_name)
        stream_info = make_stream_dict(m21_stream)
        put_in_json_dict(file_name, stream_info, force=True)
        melody_stream = simple_skyline_algorithm(m21_stream)


class MyThread (threading.Thread):
    def __init__(self, thread_id, q):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.q = q

    def run(self):
        print("Starting", self.threadID)
        run_all(self.threadID)
        print("Exiting", self.threadID)


# Todo: Throw out parts with low correlation!
# Todo: Make rests and measures!
# Todo: Save modified file


def put_in_json_dict(id: str, stream_info: dict, force: bool = False):
    json_lock.acquire()
    try:
        if not force and id in json_dict:
            json_lock.release()
            return
        if not "count" in json_dict:
            json_dict["count"] = 0
        else:
            json_dict["count"] += 1

        json_dict[id] = stream_info

        if json_dict["count"] >= 2:
            with open(JSON_FILE_PATH, 'w') as fp:
                fp.write(json.dumps(json_dict, indent=4))
            json_dict["count"] = 0
        json_lock.release()
    except:
        print(sys.exc_info())
        json_lock.release()


def make_stream_dict(m21_stream: VanillaStream):
    stream_info = {}
    stream_info["metronome_range"] = (m21_stream.metronome_mark_min, m21_stream.metronome_mark_max)
    stream_info["time_signature"] = m21_stream.time_signature
    stream_key = m21_stream.analyze('key')
    stream_info["key_and_correlation"] = (stream_key.name, stream_key.correlationCoefficient)
    parts_info = {}
    for p in m21_stream.parts:
        part_info = {}
        part_info["average_pitch"] = mean(p.pitch_list)
        part_info["average_volume"] = mean(p.volume_list)
        part_key = p.analyze('key')
        part_info["key_and_correlation"] = (part_key.name, part_key.correlationCoefficient)
        if p.total_notes_or_chords:
            part_info["note_percentage"] = p.note_number / p.total_notes_or_chords
            part_info["lyrics_percentage"] = p.lyrics_number / p.total_notes_or_chords
        else:
            part_info["note_percentage"] = 0.0
            part_info["lyrics_percentage"] = 0.0
        parts_info[p.id] = part_info
    stream_info["parts"] = parts_info

    return stream_info


exit_flag = 0
thread_number = 1

queue_lock = threading.Lock()
work_queue = queue.Queue(0)

json_lock = threading.Lock()
with open(JSON_FILE_PATH, 'r') as fp:
    json_dict = json.load(fp)

threads = []

for root, dirs, files in os.walk(Test.TEST_DATA_FOLDER.value):
    for file in files:
        if file.endswith(".mxl"):
            work_queue.put(os.path.join(root, file))
            pass

# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/aquarson.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/BA_forgive_me.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/Cant_Live_Without_You.mxl")

# Create new threads
for tName in range(thread_number - 1):
    thread = MyThread(tName + 1, work_queue)
    threads.append(thread)
    thread.start()

# Wait for queue to empty
run_all(thread_number)

# Notify threads it's time to exit
exit_flag = 1

# Wait for all threads to complete
for t in threads:
    t.join()

print("Exiting Main Thread")

sys.exit(0)
