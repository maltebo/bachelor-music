import os
import random

import numpy as np
import tensorflow as tf
import tensorflow.python.keras.callbacks as cb
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.layers import Input, LSTM, Dense, concatenate, Masking
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from tensorflow.python.keras.utils import to_categorical

import settings.constants as c
import settings.constants_preprocessing as c_p
import settings.constants_chords as c_c
import settings.constants_model as c_m
import music_utils.simple_classes as simple
import preprocessing.melody_and_chords.find_chords as chords
import preprocessing.melody_and_chords.find_melody as melody
import settings.music_info_pb2 as music_info

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = False  # to log device placement (on which device the operation ran)
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.compat.v1.Session(config=config)
set_session(sess)


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
            if file.endswith('.pb_full'):
                all_files.append(os.path.join(folder, file))

    proto_buffer = music_info.AllData()

    # import datetime
    # proto_buffer.day = datetime.datetime.now().day
    # proto_buffer.month = datetime.datetime.now().month
    # proto_buffer.year = datetime.datetime.now().year

    for i, file in enumerate(all_files):
        # print("Processing", file)
        # print("{p} percent done".format(p=(i / len(all_files)) * 100))

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


def offset_to_binary_array(offset):
    return [int(x) for x in format(int(offset), '04b')[:]]


def make_melody_data_from_file(nr_files=None):
    all_files = []
    for folder, _, files in os.walk(os.path.join(c.project_folder, "data/preprocessed_data")):
        for file in files:
            if file.endswith('.pb'):
                all_files.append(os.path.join(folder, file))
    all_files = sorted(all_files, reverse=True)

    current_pb = all_files[0]

    all_data = music_info.AllData()
    with open(current_pb, 'rb') as fp:
        all_data.ParseFromString(fp.read())

    offset_sequences = []
    length_sequences = []
    pitch_sequences = []
    next_pitches = []
    next_lengths = []
    chord_sequences = []

    if nr_files is None:
        nr_files = len(all_data.songs)

    for song_data in list(all_data.songs)[:nr_files]:

        for melody in song_data.melodies:

            if not melody.lyrics:
                print("No lyrics in file", song_data.filepath)
                continue

            offsets = list(melody.offsets)
            offsets_input = [o % 16 for o in melody.offsets]
            # -1 because shortest possible length is 1
            lengths = [e - 1 for e in melody.lengths]
            # 200 is a break (coded as pitch 200), values range in between 48 and 84 - values from 0 to 37
            pitches = [(n - 47) % (200 - 47) for n in melody.pitches]

            for i in range(len(melody.pitches)):
                current_offsets = offsets_input[max(0, i - (c_m.sequence_length)): i]
                current_lengths = lengths[max(0, i - (c_m.sequence_length)): i]
                current_pitches = pitches[max(0, i - (c_m.sequence_length)): i]

                # chord_list = []
                #
                # if current_lengths:
                #
                #     chord_list = chords[(offsets[max(0, (i - c_m.sequence_length))]//8)*8: int((((offsets[i] - 0.5)//8)*8)+8)]
                #     assert len(chord_list) >= sum(current_lengths) + len(current_lengths)
                #     assert len(chord_list) <= sum(current_lengths) + len(current_lengths) + 14
                #     assert len(chord_list) % 8 == 0
                #
                # else:
                #     chord_list = []

                offset_sequences.append(current_offsets)
                length_sequences.append(current_lengths)
                pitch_sequences.append(current_pitches)

                next_pitches.append(pitches[i])
                next_lengths.append(lengths[i])
                # chord_sequences.append([chord_list])

    return offset_sequences, length_sequences, pitch_sequences, next_pitches, next_lengths  # , chord_sequences


def melody_data_generator(data, batch_size):
    offset_sequences_o, length_sequences_o, pitch_sequences_o, next_pitches_o, next_lengths_o = zip(*data)

    random_sequence = [i for i in range(len(pitch_sequences_o))]
    np.random.shuffle(random_sequence)

    index = 0

    while True:
        length_sequences = []
        pitch_sequences = []
        offset_sequences = []

        next_pitches = []
        next_lengths = []

        while (len(pitch_sequences) < batch_size):
            length_sequences.append(length_sequences_o[random_sequence[index]])
            pitch_sequences.append(pitch_sequences_o[random_sequence[index]])
            offset_sequences.append(offset_sequences_o[random_sequence[index]])

            next_pitches.append(next_pitches_o[random_sequence[index]])
            next_lengths.append(next_lengths_o[random_sequence[index]])

            index += 1
            if index == len(random_sequence):
                np.random.shuffle(random_sequence)
                index = 0

        length_sequences = [to_categorical(length, num_classes=16) for length in length_sequences]
        pitch_sequences = [to_categorical(pitch, num_classes=38) for pitch in pitch_sequences]
        offset_sequences = [[offset_to_binary_array(o) for o in offset] for offset in offset_sequences]

        next_pitches = [to_categorical(pitch, num_classes=38) for pitch in next_pitches]
        next_lengths = [to_categorical(length, num_classes=16) for length in next_lengths]

        assert len(length_sequences) == len(pitch_sequences)
        assert len(pitch_sequences) == len(offset_sequences)
        assert len(pitch_sequences) == batch_size

        length_sequences = pad_sequences(length_sequences, maxlen=c_m.sequence_length, dtype='float32')
        pitch_sequences = pad_sequences(pitch_sequences, maxlen=c_m.sequence_length, dtype='float32')
        offset_sequences = pad_sequences(offset_sequences, maxlen=c_m.sequence_length, dtype='float32')

        # [print(e) for e in note_sequences[:5]]

        length_sequences = np.array(length_sequences)
        pitch_sequences = np.array(pitch_sequences)
        offset_sequences = np.array(offset_sequences)

        next_pitches = np.array(next_pitches)
        next_lengths = np.array(next_lengths)

        out_data = [pitch_sequences, length_sequences, offset_sequences]
        labels_out = [next_pitches, next_lengths]

        yield out_data, labels_out


def melody_model(validation_split=0.2, batch_size=32, epochs=1, nr_files=None, callbacks=False):
    fit = input("Fit melody model? Y/n")

    if fit != 'Y':
        return

    offset_sequences_o, length_sequences_o, pitch_sequences_o, next_pitches_o, next_lengths_o = \
        make_melody_data_from_file(nr_files=nr_files)

    ##########################################################################################
    ################# MODEL
    ##########################################################################################

    pitch_input = Input(shape=(c_m.sequence_length, 38), dtype='float32', name='pitch_input')
    length_input = Input(shape=(c_m.sequence_length, 16), dtype='float32', name='length_input')
    offset_input = Input(shape=(c_m.sequence_length, 4), dtype='float32', name='offset_input')

    concatenated_input = concatenate([pitch_input, length_input, offset_input], axis=-1)

    masked_input = Masking(0.0)(concatenated_input)

    lstm_layer = LSTM(256)(masked_input)

    pitch_output = Dense(38, activation='softmax', name='pitch_output')(lstm_layer)
    length_output = Dense(16, activation='softmax', name='length_output')(lstm_layer)

    model = Model(inputs=[pitch_input, length_input, offset_input],
                  outputs=[pitch_output, length_output])

    model.compile(loss={'pitch_output': 'categorical_crossentropy',
                        'length_output': 'categorical_crossentropy'},
                  optimizer=Adam())

    print(model.summary(90))

    ##########################################################################################
    ################# CALLBACKS
    ##########################################################################################

    if callbacks:
        terminate_on_nan = cb.TerminateOnNaN()

        import datetime
        time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filepath = "data/tf_weights/melody-weights-improvement{t}.hdf5".format(t=time)
        checkpoint = cb.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='min')

        early_stopping = cb.EarlyStopping(monitor='val_loss', min_delta=0, patience=5,
                                          verbose=0, mode='auto', baseline=None)

        tensorboard = cb.TensorBoard(log_dir=os.path.join(c.project_folder, "data/tensorboard_logs"),
                                     histogram_freq=1, batch_size=32, write_graph=True, write_grads=True,
                                     write_images=True, embeddings_freq=0, embeddings_layer_names=None,
                                     embeddings_metadata=None, embeddings_data=None)

        reduce_lr = cb.ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                                         patience=3, min_lr=0.001)

        callbacks = [terminate_on_nan, checkpoint, early_stopping, tensorboard, reduce_lr]
    else:
        callbacks = []

    ##########################################################################################
    ################# DATA PREPARATION
    ##########################################################################################

    zipped_data = list(zip(offset_sequences_o, length_sequences_o, pitch_sequences_o,
                           next_pitches_o, next_lengths_o))

    assert validation_split < 1 and validation_split >= 0

    random.shuffle(zipped_data)
    test_data = zipped_data[:int(len(zipped_data) * validation_split)]
    train_data = zipped_data[int(len(zipped_data) * validation_split):]

    model.fit_generator(generator=melody_data_generator(train_data, batch_size),
                        steps_per_epoch=len(train_data) // batch_size,
                        epochs=epochs, verbose=1, validation_data=melody_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=30, callbacks=callbacks)


def make_chord_data_from_file(nr_files=None):
    all_files = []
    for folder, _, files in os.walk(os.path.join(c.project_folder, "data/preprocessed_data")):
        for file in files:
            if file.endswith('.pb'):
                all_files.append(os.path.join(folder, file))
    all_files = sorted(all_files, reverse=True)

    current_pb = all_files[0]

    all_data = music_info.AllData()
    with open(current_pb, 'rb') as fp:
        all_data.ParseFromString(fp.read())

    chord_sequences = []
    melody_sequences = []
    start_sequences = []
    next_chords = []

    if nr_files is None:
        nr_files = len(all_data.songs)

    for song_data in list(all_data.songs)[:nr_files]:

        chords = list(song_data.chords)
        melody_list = np.zeros(8 * len(chords))
        start_list = np.zeros(8 * len(chords))

        for melody in song_data.melodies:
            # 200 is a break (coded as pitch 200), values range in between 48 and 84 - values from 0 to 37
            pitches = [(n - 47) % (200 - 47) for n in melody.pitches]

            for pitch, length, offset in zip(pitches, melody.lengths, melody.offsets):
                melody_list[offset:offset + length] = pitch
                start_list[offset] = 1

        for i in range(len(chords)):
            current_chords = chords[max(0, i - (c_m.chord_sequence_length)): i]
            current_pitches = melody_list[i * 8: (i + 1) * 8]
            current_starts = start_list[i * 8: (i + 1) * 8]

            assert len(current_pitches) == 8
            assert len(current_starts) == 8

            chord_sequences.append(current_chords)
            melody_sequences.append(current_pitches)
            start_sequences.append(current_starts)

            next_chords.append(chords[i])

    on_full_beat = [[i % 2, (i + 1) % 2] for i in range(len(chord_sequences))]
    # 1,0 is full beat, 0,1 is half beat

    return chord_sequences, melody_sequences, start_sequences, on_full_beat, next_chords


def chord_data_generator(data, batch_size):
    chord_sequences, melody_sequences, start_sequences, on_full_beat, next_chords = zip(*data)

    random_sequence = [i for i in range(len(chord_sequences))]
    np.random.shuffle(random_sequence)

    index = 0

    while True:
        chords = []
        melody = []
        start = []
        on_beat = []
        labels = []

        while (len(chords) < batch_size):
            chords.append(chord_sequences[random_sequence[index]])
            melody.append(melody_sequences[random_sequence[index]])
            start.append(start_sequences[random_sequence[index]])
            on_beat.append(on_full_beat[random_sequence[index]])

            labels.append(next_chords[random_sequence[index]])

            index += 1
            if index == len(random_sequence):
                np.random.shuffle(random_sequence)
                index = 0

        chords = [to_categorical(chord, num_classes=25) for chord in chords]

        melody = [to_categorical(pitch, num_classes=38) for pitch in melody]
        chords = pad_sequences(chords, maxlen=c_m.chord_sequence_length, dtype='float32')

        melody = np.reshape(melody, (-1, 8 * 38))

        labels = [to_categorical(label, num_classes=25) for label in labels]

        chords = np.array(chords)
        melody = np.array(melody)
        start = np.array(start)
        on_beat = np.array(on_beat)
        labels = np.array(labels)

        out_data = [chords, melody, start, on_beat]

        yield out_data, labels


def chord_model(validation_split=0.2, batch_size=32, epochs=1, nr_files=None, callbacks=False):
    fit = input("Fit chord model? Y/n")
    if fit != 'Y':
        return

    chord_sequences, melody_sequences, start_sequences, on_full_beat, next_chords \
        = make_chord_data_from_file(nr_files=nr_files)

    ##########################################################################################
    ################# MODEL
    ##########################################################################################

    chord_input = Input(shape=(c_m.chord_sequence_length, 25), dtype='float32', name='chord_input')
    melody_input = Input(shape=(8 * 38,), dtype='float32', name='melody_input')
    start_input = Input(shape=(8,), dtype='float32', name='start_input')
    on_full_beat_input = Input(shape=(2,), dtype='float32', name='on_full_beat_input')

    concatenate_pre = concatenate([melody_input, start_input, on_full_beat_input], axis=-1)

    dense_pre = Dense(32, activation='relu', name='dense_pre')(concatenate_pre)

    masked_input = Masking(0.0)(chord_input)

    lstm = LSTM(64)(masked_input)

    concatenate_final = concatenate([dense_pre, lstm], axis=-1)

    dense_final = Dense(25, activation='softmax', name='dense_final')(concatenate_final)

    model = Model(inputs=[chord_input, melody_input, start_input, on_full_beat_input],
                  outputs=[dense_final])

    model.compile(loss={'dense_final': 'categorical_crossentropy'},
                  optimizer=Adam())

    print(model.summary(90))

    ##########################################################################################
    ################# CALLBACKS
    ##########################################################################################

    if callbacks:
        terminate_on_nan = cb.TerminateOnNaN()

        import datetime
        time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filepath = "data/tf_weights/chords-weights-improvement{t}.hdf5".format(t=time)
        checkpoint = cb.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='min')

        early_stopping = cb.EarlyStopping(monitor='val_loss', min_delta=0, patience=5,
                                          verbose=0, mode='auto', baseline=None)

        tensorboard = cb.TensorBoard(log_dir=os.path.join(c.project_folder, "data/tensorboard_logs"),
                                     histogram_freq=1, batch_size=32, write_graph=True, write_grads=True,
                                     write_images=True, embeddings_freq=0, embeddings_layer_names=None,
                                     embeddings_metadata=None, embeddings_data=None)

        reduce_lr = cb.ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                                         patience=3, min_lr=0.001)

        callbacks = [terminate_on_nan, checkpoint, early_stopping, tensorboard, reduce_lr]
    else:
        callbacks = []

    ##########################################################################################
    ################# DATA PREPARATION
    ##########################################################################################

    zipped_data = list(zip(chord_sequences, melody_sequences, start_sequences,
                           on_full_beat, next_chords))

    assert validation_split < 1 and validation_split >= 0

    random.shuffle(zipped_data)
    test_data = zipped_data[:int(len(zipped_data) * validation_split)]
    train_data = zipped_data[int(len(zipped_data) * validation_split):]

    ##########################################################################################
    ################# MODEL FITTING
    ##########################################################################################

    model.fit_generator(generator=chord_data_generator(train_data, batch_size),
                        steps_per_epoch=len(train_data) // batch_size,
                        epochs=epochs, verbose=1, validation_data=chord_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=30,
                        callbacks=callbacks)


if __name__ == '__main__':
    # make_pb_for_lyrics_files()
    # chord_model(nr_files=None, callbacks=False)
    # melody_model(nr_files=5, callbacks=False)
    # os.makedirs(os.path.join(c.project_folder, 'data/protobuffer_data'), exist_ok=True)
    # make_pb_for_all_files()

    make_protobuffer_for_all_data()
