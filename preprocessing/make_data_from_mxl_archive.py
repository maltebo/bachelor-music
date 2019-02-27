#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.abspath(".."))
import preprocessing.constants as c
from preprocessing.create_modified_stream import process_data
from preprocessing.find_melody import simple_skyline_algorithm
from preprocessing.make_info import make_stream_dict
from preprocessing.make_info import put_in_json_dict
from preprocessing.make_info import valid_entry_exists
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


def run_all(thread_nr):
    while not work_queue.empty():
        force_dict = True
        update = True
        # Todo change value
        file_name = get_job(work_queue)

        if not file_name:
            continue
        if not force_dict and valid_entry_exists(file_name):
            continue

        m21_stream = process_data(thread_nr, file_name)
        stream_info = make_stream_dict(m21_stream)

        if update:
            put_in_json_dict(file_name, stream_info, force=force_dict)
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


exit_flag = 0
thread_number = 5

queue_lock = threading.Lock()
work_queue = queue.Queue(0)


threads = []

for root, dirs, files in os.walk(c.Test.TEST_DATA_FOLDER.value):
    for file in files:
        if file.endswith(".mxl"):
            work_queue.put(os.path.join(root, file))
            pass

# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/aquarson.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/BA_forgive_me.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/Cant_Live_Without_You.mxl")
# work_queue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/bwv861.mxl")

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
