#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.abspath(".."))
import settings.constants as c
from preprocessing.helper import FileNotFittingSettingsError
from preprocessing.create_modified_stream import process_data
from preprocessing.create_modified_stream import make_key_and_correlations
from preprocessing.make_info import put_in_protocol_buffer, add_notes_to_protocol_buffer
from preprocessing.make_info import proto_buffer_entry_exists
from preprocessing.vanilla_stream import VanillaStream
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
        filename = get_job(work_queue)

        if not filename:
            continue
        if proto_buffer_entry_exists(filename):
            continue

        m21_stream = VanillaStream(filename)

        try:
            process_data(thread_nr, m21_stream)
            make_key_and_correlations(m21_stream)
            m21_stream.valid = True

            if c.UPDATE:
                put_in_protocol_buffer(m21_stream)

            # in the skyline algorithm it is asserted that the melody is a sequence
            # melody_stream = simple_skyline_algorithm(m21_stream)
            #
            # melody_struct = get_tf_structure(melody_stream)
            # save_melody_struct(filename, melody_struct)

            # melody_stream.show('midi')

            # full_stream = find_chords(m21_stream, melody_stream)
        except FileNotFittingSettingsError:
            if c.UPDATE:
                put_in_protocol_buffer(m21_stream, error_message=sys.exc_info()[1])
            print(filename, sys.exc_info()[1])


def add_missing_note_info(thread_nr: int):
    """
    adds notes to all parts of valid files that are missing the note information.
    might not need to be used in the future
    :param thread_nr: For printing status information
    :return:
    """
    while not work_queue.empty():
        piece_of_music = get_job(work_queue)

        if not piece_of_music:
            continue

        if not piece_of_music.valid:
            continue

        if piece_of_music.parts[0].notes:
            continue

        try:
            m21_stream = VanillaStream(piece_of_music.filepath)

            process_data(thread_nr, m21_stream)
            make_key_and_correlations(m21_stream)
        except FileNotFittingSettingsError:
            piece_of_music.valid = False
            piece_of_music.error_message = str(sys.exc_info()[1])
            continue

        c.music_info_dict_lock.acquire()

        for part in piece_of_music.parts:
            stop = False
            for p in m21_stream.parts:
                if p.partName == part.name:
                    add_notes_to_protocol_buffer(part, p)
                    stop = True
            assert stop

        c.music_protocol_buffer.counter += 1

        if c.music_protocol_buffer.counter >= 1:
            print("write protocol buffer")
            with open(c.PROTOCOL_BUFFER_LOCATION, 'wb') as fp:
                fp.write(c.music_protocol_buffer.SerializeToString())
            c.music_protocol_buffer.counter = 0

        c.music_info_dict_lock.release()


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

# for root, dirs, files in os.walk(c.TEST_DATA_FOLDER):
#     for file in files:
#         if file.endswith(".mxl"):
#             work_queue.put(os.path.join(root, file))
#             pass
for value in c.music_protocol_buffer.music_data:
    work_queue.put(value)

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
