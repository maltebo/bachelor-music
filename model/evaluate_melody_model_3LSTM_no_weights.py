import os
import random
import sys

import numpy as np
import tensorflow as tf
import keras.callbacks as call_backs
from keras.backend import set_session
from keras.layers import Input, LSTM, Dense, concatenate, Masking, Dropout, Reshape
from keras.models import Model, load_model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

import settings.constants as c
import settings.constants_model as c_m
import settings.music_info_pb2 as music_info
from model.custom_callbacks import ModelCheckpointBatches, ModelCheckpoint
import model.converting as converter

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = False  # to log device placement (on which device the operation ran)
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.compat.v1.Session(config=config)
set_session(sess)

force = False


def make_melody_data_from_file(nr_files=None):
    all_files = []

    all_data = c_m.all_data

    offsets_out = []
    length_sequences = []
    pitch_sequences = []
    next_pitches = []
    next_lengths = []
    chord_sequences = []

    if nr_files is None:
        nr_files = len(all_data.songs)

    for song_data in list(all_data.songs)[:nr_files]:

        for melody in song_data.melodies:

            offsets = list(melody.offsets)
            offsets_input = [o % 16 for o in melody.offsets]
            # -1 because shortest possible length is 1
            lengths = [converter.length_to_id[e] for e in melody.lengths]
            # 200 is a break (coded as pitch 200), values range in between 48 and 84 - values from 0 to 37
            pitches = [converter.pitch_to_id[n] for n in melody.pitches]

            for i in range(len(melody.pitches)):
                current_lengths = lengths[max(0, i - (c_m.sequence_length)): i]
                current_pitches = pitches[max(0, i - (c_m.sequence_length)): i]

                offsets_out.append(offsets_input[i])
                length_sequences.append(current_lengths)
                pitch_sequences.append(current_pitches)

                next_pitches.append(pitches[i])
                next_lengths.append(lengths[i])
                # chord_sequences.append([chord_list])
    del all_data

    assert len(offsets_out) == len(length_sequences) == len(pitch_sequences) == len(next_pitches) == len(next_lengths)

    return offsets_out, length_sequences, pitch_sequences, next_pitches, next_lengths  # , chord_sequences


def melody_data_generator(data, batch_size):
    offsets_o, length_sequences_o, pitch_sequences_o, next_pitches_o, next_lengths_o = zip(*data)

    random_sequence = [i for i in range(len(pitch_sequences_o))]
    np.random.shuffle(random_sequence)

    index = 0

    while True:
        length_sequences = []
        pitch_sequences = []
        offsets = []

        next_pitches = []
        next_lengths = []

        while (len(pitch_sequences) < batch_size):
            length_sequences.append(length_sequences_o[random_sequence[index]])
            pitch_sequences.append(pitch_sequences_o[random_sequence[index]])

            offsets.append(offsets_o[random_sequence[index]])

            next_pitches.append(next_pitches_o[random_sequence[index]])
            next_lengths.append(next_lengths_o[random_sequence[index]])

            index += 1
            if index == len(random_sequence):
                np.random.shuffle(random_sequence)
                index = 0

        length_sequences = [to_categorical(length, num_classes=16) for length in length_sequences]
        pitch_sequences = [to_categorical(pitch, num_classes=38) for pitch in pitch_sequences]
        offsets = [converter.offset_to_binary_array(o) for o in offsets]

        next_pitches = [to_categorical(pitch, num_classes=38) for pitch in next_pitches]
        next_lengths = [to_categorical(length, num_classes=16) for length in next_lengths]
        assert len(length_sequences) == len(pitch_sequences)
        assert len(pitch_sequences) == batch_size
        assert len(offsets) == len(length_sequences)

        length_sequences = pad_sequences(length_sequences, maxlen=c_m.sequence_length, dtype='float32')
        pitch_sequences = pad_sequences(pitch_sequences, maxlen=c_m.sequence_length, dtype='float32')

        # [print(e) for e in note_sequences[:5]]

        length_sequences = np.array(length_sequences)
        pitch_sequences = np.array(pitch_sequences)
        offsets = np.array(offsets)

        next_pitches = np.array(next_pitches)
        next_lengths = np.array(next_lengths)

        out_data = [pitch_sequences, length_sequences, offsets]
        labels_out = [next_pitches, next_lengths]

        yield out_data, labels_out

pitch_weights = {i+1:1 for i in range(47)}

pitch_weights[0] = 0.7

length_weights = None

def melody_model(save_path, validation_split=0.1, batch_size=32):

    offsets_o, length_sequences_o, pitch_sequences_o, next_pitches_o, next_lengths_o = \
        make_melody_data_from_file(nr_files=None)

    ##########################################################################################
    ################# MODEL
    ##########################################################################################

    model = load_model(save_path)

    ##########################################################################################
    ################# DATA PREPARATION
    ##########################################################################################

    zipped_data = list(zip(offsets_o, length_sequences_o, pitch_sequences_o,
                           next_pitches_o, next_lengths_o))

    del offsets_o
    del length_sequences_o
    del pitch_sequences_o
    del next_pitches_o
    del next_lengths_o

    assert validation_split < 1 and validation_split >= 0

    test_data = zipped_data[:int(len(zipped_data) * validation_split)]
    train_data = zipped_data[int(len(zipped_data) * validation_split):]

    print("Number of data points in training data:", len(train_data))
    print("Number of data points in validaion data:", len(test_data))
    print("Batch size:", int(batch_size))
    print("Steps in an epoch:", int(len(train_data) // batch_size))

    del zipped_data

    verbose = 1
    if force:
        verbose = 0

    result_train = model.evaluate_generator(generator=melody_data_generator(train_data, batch_size),
                        steps=len(train_data) // batch_size,
                        max_queue_size=32)

    print("RESULT_TRAIN:", result_train, flush=True)

    result_val = model.evaluate_generator(generator=melody_data_generator(test_data, batch_size),
                        steps=len(test_data) // batch_size,
                        max_queue_size=32)

    print("RESULT_VALIDATION:", result_val, flush=True)


if __name__ == '__main__':

    melody_model(save_path=os.path.join(c.project_folder,
                                        "data/tf_weights/m3nw/melody-weights-3LSTMnw-improvement-472-vl-2.64893-vpacc-0.47701-vlacc-0.66466.hdf5"),
                 validation_split=0.1,
                 batch_size=32)