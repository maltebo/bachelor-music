import numpy as np

import music_utils.simple_classes as simple
import preprocessing.melody_and_chords.find_melody as melody
import settings.constants as c
import settings.music_info_pb2 as music_info


def make_melody_data():
    pass


def make_chords_data():
    pass


def run_all():
    my_work_queue = c.proto_buffer_work_queue

    for i in range(42):
        filename = my_work_queue.get()

        assert filename.endswith('.pb')

        print(filename)

        with open(filename, 'rb') as fp:
            proto_buffer = music_info.VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        lyrics, full_melody = melody.skyline_advanced(simple_song, split=False)

        if not full_melody or not full_melody[0][1]:
            continue

        # print(full_melody[0][1])

        song_pb = music_info.SongData()
        song_pb.filepath = filename

        ##################################################################################
        # create melody protobuffer
        ##################################################################################

        for m in full_melody:
            melody_pb = song_pb.melodies.add()

            melody_pb.lyrics = lyrics

            try:
                note_info = np.array(m[1])
            except:
                print("OH NOOOOOOOO")
                print(full_melody)
                import sys
                import traceback
                traceback.print_exc()
                sys.exit(-1)

            try:
                offsets = [int(m[0] + elem * 4) for elem in note_info[:, 0]]
                lengths = [int(elem * 4) for elem in note_info[:, 1]]
                pitches = [int(elem) for elem in note_info[:, 2]]
                volumes = [int(elem) for elem in note_info[:, 3]]
                melody_pb.offsets.extend(offsets)
                melody_pb.lengths.extend(lengths)
                melody_pb.pitches.extend(pitches)
                melody_pb.volumes.extend(volumes)
            except:
                print("SOMETHING WENT WRONG")
                print(full_melody)
                print(m)
                import sys
                import traceback
                traceback.print_exc()
                sys.exit(-1)

        ##################################################################################
        # create chord protobuffer
        ##################################################################################


if __name__ == '__main__':
    run_all()
