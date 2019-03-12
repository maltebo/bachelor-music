#!/usr/bin/env python3
import os
import random
import sys
import threading
import time

import settings.constants as c
from analyze_and_modify.create_modified_stream import make_key_and_correlations
from analyze_and_modify.create_modified_stream import process_data
from analyze_and_modify.make_info import proto_buffer_entry_exists, save_vanilla_stream_pb
from analyze_and_modify.make_info import put_in_protocol_buffer
from music_utils.vanilla_stream import VanillaStream
from preprocessing.helper import FileNotFittingSettingsError


class MakeDataThread(threading.Thread):
    def __init__(self, thread_id=random.randint(100000, 999999)):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.work_queue = c.make_data_work_queue
        self.queue_lock = c.make_data_work_queue_lock
        self.exit_flag = 0

    def run(self):
        print("Starting", self.threadID)
        self.run_analyze_and_create_data()
        print("Exiting", self.threadID)

    def stop(self):
        self.exit_flag = 1

    def get_job(self) -> str:
        self.queue_lock.acquire()
        if not self.work_queue.empty():
            file_name = self.work_queue.get()
            self.queue_lock.release()
            return file_name

        else:
            self.queue_lock.release()
            time.sleep(1)
            return ""

    def run_analyze_and_create_data(self):
        """
        1. loads a file and creates a corresponding VanillaStream.
        2. saves the file information in the global protocol buffer
        3. saves a local pb file at the same place where the original
           file was located, with .pb ending
        :return:
        """
        while not self.work_queue.empty() and not self.exit_flag:
            filename = self.get_job()

            if not filename:
                continue

            exists, valid = proto_buffer_entry_exists(filename)
            if exists and not valid:
                continue

            if os.path.exists(filename.replace('.mxl', '.pb')):
                continue

            m21_stream = VanillaStream(filename)

            try:
                process_data(self.threadID, m21_stream)
                make_key_and_correlations(m21_stream)
                m21_stream.valid = True

                if c.UPDATE and not exists:
                    put_in_protocol_buffer(m21_stream)

                save_vanilla_stream_pb(m21_stream)

                # in the skyline algorithm it is asserted that the melody is a sequence
                # melody_stream = simple_skyline_algorithm(m21_stream)
                #
                # melody_struct = get_tf_structure(melody_stream)
                # save_melody_struct(filename, melody_struct)

                # melody_stream.show('midi')

                # full_stream = find_chords(m21_stream, melody_stream)
            except FileNotFittingSettingsError:
                if valid:
                    m21_stream.show('text')
                    print(sys.exc_info()[1])
                    continue
                if c.UPDATE and not exists:
                    put_in_protocol_buffer(m21_stream, error_message=str(sys.exc_info()[1]))
                print(filename, sys.exc_info()[1])


if __name__ == "__main__":
    thread_number = 4
    threads = []

    for tName in range(thread_number):
        thread = MakeDataThread(tName + 1)
        threads.append(thread)
        thread.start()

    # print("\n\nstart sleeping\n\n")
    #
    # time.sleep(1000)
    #
    # print("\n\nstop sleeping\n\n")
    #
    # for t in threads:
    #     t.stop()
    #
    # print("\n\nstopped all threads\n\n")

    for t in threads:
        t.join()

    # print("\n\nend test")

    sys.exit(0)
