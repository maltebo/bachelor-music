import os

import numpy as np

import settings.constants as c
import settings.constants_preprocessing as c_p
import settings.constants_chords as c_c
import music_utils.simple_classes as simple
import preprocessing.melody_and_chords.find_chords as chords
import preprocessing.melody_and_chords.find_melody as melody
import settings.music_info_pb2 as music_info


def make_pb_for_all_files():

    my_work_queue = c_p.proto_buffer_work_queue

    work = False

    while not my_work_queue.empty():

        filename = my_work_queue.get()

        assert filename.endswith('.pb')

        new_filename = filename.replace('.pb', '.pb_full_final')
        new_filename = new_filename.replace('protobuffer', 'protobuffer_data')

        if os.path.exists(new_filename):
            continue

        print(filename)

        with open(filename, 'rb') as fp:
            proto_buffer = music_info.VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        lyrics, full_melody = melody.skyline_advanced(simple_song, split=True)

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
                offsets = [int(m[0] * 4 + elem * 4) for elem in note_info[:, 0]]
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

            split_song = chords.split_in_areas(simple_song)

            song_chords = chords.get_corresponding_chords(split_song)

            song_chords = [c_c.chord_to_id[ch] for ch in song_chords]

            song_pb.chords.extend(song_chords)

        with open(new_filename, 'xb') as fp:
            fp.write(song_pb.SerializeToString())

def make_pb_for_lyrics_files():
    start = input("Really? This will delete some files. Go on? Y/n")
    if start != 'Y':
        return


    my_work_queue = c_p.proto_buffer_work_queue

    work = False

    while not my_work_queue.empty():

        filename = my_work_queue.get()

        assert filename.endswith('.pb')

        print(filename)

        with open(filename, 'rb') as fp:
            proto_buffer = music_info.VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        lyrics, full_melody = melody.skyline_advanced(simple_song, split=True)

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

            if lyrics:
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
                    offsets = [int(m[0] * 4 + elem * 4) for elem in note_info[:, 0]]
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

            split_song = chords.split_in_areas(simple_song)

            song_chords = chords.get_corresponding_chords(split_song)

            song_chords = [c_c.chord_to_id[ch] for ch in song_chords]

            song_pb.chords.extend(song_chords)

        new_filename = filename.replace('.pb', '.pb_full')

        try:
            os.remove(new_filename)
        except:
            pass

        if lyrics:
            with open(new_filename, 'xb') as fp:
                fp.write(song_pb.SerializeToString())


def make_protobuffer_for_all_data():
    all_files = []
    for folder, _, files in os.walk(c_c.TRANSFORMED_PROTO_BUFFER_PATH):
        for file in files:
            if file.endswith('.pb_full_final'):
                all_files.append(os.path.join(folder, file))

    proto_buffer = music_info.AllData()

    import datetime
    proto_buffer.day = datetime.datetime.now().day
    proto_buffer.month = datetime.datetime.now().month
    proto_buffer.year = datetime.datetime.now().year

    for i, file in enumerate(all_files):
        print("Processing", file)
        print("{p} percent done".format(p=(i / len(all_files)) * 100))

        song_data = proto_buffer.songs.add()
        with open(file, 'rb') as fp:
            song_data.ParseFromString(fp.read())

    try:
        with open(os.path.join(c.project_folder,
                               "data/preprocessed_data/data_{y}_{m}_{d}.pb".format(y=proto_buffer.year,
                                                                                   m=proto_buffer.month,
                                                                                   d=proto_buffer.day)), 'xb') as fp:
            fp.write(proto_buffer.SerializeToString())
    except FileExistsError:
        ow = input("File already exists! Do you want to overwrite it? Y/n")
        if ow == 'Y':
            with open(os.path.join(c.project_folder,
                                   "data/preprocessed_data/data_{y}_{m}_{d}.pb".format(y=proto_buffer.year,
                                                                                       m=proto_buffer.month,
                                                                                       d=proto_buffer.day)),
                      'wb') as fp:
                fp.write(proto_buffer.SerializeToString())



if __name__ == '__main__':
    # make_pb_for_lyrics_files()
    # chord_model(nr_files=None, callbacks=False)
    # melody_model(nr_files=5, callbacks=False)
    # os.makedirs(os.path.join(c.project_folder, 'data/protobuffer_data'), exist_ok=True)
    # make_pb_for_all_files()

    make_protobuffer_for_all_data()
