#!/usr/bin/env python3

import random
import sys
import threading
import time

import settings.constants as c
from analyze_and_modify.create_modified_stream import make_key_and_correlations
from analyze_and_modify.create_modified_stream import process_data
from analyze_and_modify.make_info import proto_buffer_entry_exists
from analyze_and_modify.make_info import put_in_protocol_buffer, add_notes_to_protocol_buffer
from m21_utils.vanilla_stream import VanillaStream
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

    def get_job(self):
        self.queue_lock.acquire()
        if not self.work_queue.empty():
            file_name = self.work_queue.get()
            self.queue_lock.release()
            return file_name

        else:
            self.queue_lock.release()
            time.sleep(1)
            return None

    def run_analyze_and_create_data(self):
        """
        runs all implemented steps for preprocessing as long as there is something to do
        :return:
        """
        while not self.work_queue.empty() and not self.exit_flag:
            filename = self.get_job()

            if not filename:
                continue
            if proto_buffer_entry_exists(filename):
                continue

            m21_stream = VanillaStream(filename)

            try:
                process_data(self.threadID, m21_stream)
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

    def add_missing_note_info(self):
        """
        adds notes to all parts of valid files that are missing the note information.
        might not need to be used in the future
        :return:
        """
        while not self.work_queue.empty():
            piece_of_music = self.get_job()

            if not piece_of_music:
                continue

            if not piece_of_music.valid:
                continue

            if piece_of_music.parts[0].notes:
                continue

            try:
                m21_stream = VanillaStream(piece_of_music.filepath)

                process_data(self.threadID, m21_stream)
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

            if c.music_protocol_buffer.counter >= 10:
                print("write protocol buffer")
                with open(c.PROTOCOL_BUFFER_LOCATION, 'wb') as fp:
                    fp.write(c.music_protocol_buffer.SerializeToString())
                c.music_protocol_buffer.counter = 0

            c.music_info_dict_lock.release()


if __name__ == "__main__":
    thread_number = 8
    threads = []
    c.UPDATE = False

    for tName in range(thread_number):
        thread = MakeDataThread(tName + 1)
        threads.append(thread)
        thread.start()

    print("\n\nstart sleeping\n\n")

    time.sleep(10)

    print("\n\nstop sleeping\n\n")

    for t in threads:
        t.stop()

    print("\n\nstopped all threads\n\n")

    for t in threads:
        t.join()

    print("\n\nend test")

    sys.exit(0)
