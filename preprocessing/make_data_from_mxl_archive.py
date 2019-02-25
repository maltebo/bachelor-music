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


def get_job(temp_queue):
    queueLock.acquire()
    if not workQueue.empty():
        file_name = temp_queue.get()
        queueLock.release()
        return file_name

    else:
        queueLock.release()
        time.sleep(1)
        return None


def run_all(thread_nr):
    while not workQueue.empty():
        file_name = get_job(workQueue)
        if not file_name:
            continue
        m21_stream = process_data(thread_nr, file_name)
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


def add_statistics_to_json(m21_stream: VanillaStream):
    pass


exit_flag = 0
thread_number = 1

queueLock = threading.Lock()
workQueue = queue.Queue(0)

jsonLock = threading.Lock()
with open(JSON_FILE_PATH, 'r') as fp:
    json_dict = json.load(fp)

threads = []

for root, dirs, files in os.walk(Test.TEST_DATA_FOLDER.value):
    for file in files:
        if file.endswith(".mxl"):
            # workQueue.put(os.path.join(root, file))
            pass

workQueue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/4_4/aquarson.mxl")
workQueue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/BA_forgive_me.mxl")
workQueue.put("/home/malte/PycharmProjects/BachelorMusic/data/MXL_raw/test_file.mxl")

# Create new threads
for tName in range(thread_number - 1):
    thread = MyThread(tName + 1, workQueue)
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
