#!/usr/bin/env python3

import os
import sys


sys.path.append(os.path.abspath(".."))
import preprocessing.constants as c
from preprocessing.helper import FileNotFittingSettingsError
from preprocessing.create_modified_stream import process_data
from preprocessing.create_modified_stream import make_key_and_correlations
from preprocessing.find_melody import simple_skyline_algorithm
from preprocessing.make_info import make_stream_dict
from preprocessing.make_info import put_in_json_dict
from preprocessing.make_info import valid_entry_exists
from preprocessing.make_tf_structure import get_tf_structure, save_melody_struct
import threading
import queue
import time


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


def run_all(thread_nr: int):
    """
    runs all implemented steps for preprocessing as long as there is something to do
    :param thread_nr: For printing status information
    :return:
    """
    while not work_queue.empty():
        file_name = get_job(work_queue)

        if not file_name:
            continue
        if not c.FORCE and valid_entry_exists(file_name):
            continue

        try:
            m21_stream = process_data(thread_nr, file_name)
            make_key_and_correlations(m21_stream)
            stream_info = make_stream_dict(m21_stream)

            if c.UPDATE:
                put_in_json_dict(file_name, stream_info)

            # in the skyline algorithm it is asserted that the melody is a sequence
            melody_stream = simple_skyline_algorithm(m21_stream)

            melody_struct = get_tf_structure(melody_stream)
            save_melody_struct(file_name, melody_struct)

            # melody_stream.show('midi')

            # full_stream = find_chords(m21_stream, melody_stream)
        except FileNotFittingSettingsError:
            print(file_name, sys.exc_info()[1])


def analyze_note_lengths(thread_nr: int):
    while not work_queue.empty():
        file_name = get_job(work_queue)

        if not file_name:
            continue
        if not c.FORCE and valid_entry_exists(file_name):
            continue

        m21_stream = process_data(thread_nr, file_name)
        make_key_and_correlations(m21_stream)
        stream_info = make_stream_dict(m21_stream)

        # in the skyline algorithm it is asserted that the melody is a sequence
        melody_stream = simple_skyline_algorithm(m21_stream)
        local_dict = {}

        for n in melody_stream.flat.notes:
            if n.quarterLength in local_dict:
                local_dict[n.quarterLength] += 1
            else:
                local_dict[n.quarterLength] = 1

        note_lengths_lock.acquire()
        for key in local_dict:
            if key in note_lengths_dict:
                note_lengths_dict[key] += local_dict[key]
            else:
                note_lengths_dict[key] = local_dict[key]
        if thread_nr == 1:
            print(note_lengths_dict)
        note_lengths_lock.release()


class MyThread (threading.Thread):
    def __init__(self, thread_id, q):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.q = q

    def run(self):
        print("Starting", self.threadID)
        current_job(self.threadID)
        print("Exiting", self.threadID)


exit_flag = 0
thread_number = 8

current_job = run_all

queue_lock = threading.Lock()
work_queue = queue.Queue(0)

threads = []

for root, dirs, files in os.walk(c.TEST_DATA_FOLDER):
    for file in files:
        if file.endswith(".mxl"):
            work_queue.put(os.path.join(root, file))
            pass

# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL/TestData/Affairs1.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL/TestData/Bwv0540_Toccata_and_Fugue.mxl")

# Create new threads
for tName in range(thread_number - 1):
    thread = MyThread(tName + 1, work_queue)
    threads.append(thread)
    thread.start()

note_lengths_dict = {}
note_lengths_lock = threading.Lock()

# Wait for queue to empty
current_job(thread_number)

# Notify threads it's time to exit
exit_flag = 1

# Wait for all threads to complete
for t in threads:
    t.join()

print("Exiting Main Thread")

sys.exit(0)
