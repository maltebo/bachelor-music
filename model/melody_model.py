import os
import random
import sys

import numpy as np
import tensorflow as tf
import keras.callbacks as cb
from keras.backend import set_session
from keras.layers import Input, LSTM, Dense, concatenate, Masking
from keras.models import Model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

import settings.constants as c
import settings.constants_model as c_m
import settings.music_info_pb2 as music_info

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = False  # to log device placement (on which device the operation ran)
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.compat.v1.Session(config=config)
set_session(sess)

force = False

def offset_to_binary_array(offset):
    return [int(x) for x in format(int(offset), '04b')[:]]


def make_melody_data_from_file(nr_files=None):
    all_files = []

    all_data = c_m.all_data

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
    del all_data

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

pitch_weights = {
    0: 0.7999507265060386,
    20: 0.8185322468244942,
    17: 0.8292360160956724,
    13: 0.841119535307133,
    25: 0.8488605807980031,
    15: 0.8582555876853357,
    22: 0.8863788241731292,
    27: 0.8918502331707752,
    29: 0.8923198793798044,
    18: 0.9014639635420608,
    8: 0.9024220125238418,
    32: 0.9391996525640948,
    24: 0.9745647640821913,
    10: 0.9930600229183225,
    12: 1.0331210235688348,
    30: 1.050019183417216,
    5: 1.1379724404914993,
    34: 1.2007564988097825,
    37: 1.2580090850260426,
    3: 1.2940959553613365,
    6: 1.3503431009315179,
    1: 1.3697163397791114,
    36: 1.6210836585055795,
    19: 1.7683765926254322,
    23: 1.89817399775069,
    16: 2.5121499400675606,
    11: 2.546669807170125,
    21: 2.6078503908422057,
    31: 2.8659467508269483,
    28: 3.2121569690252016,
    26: 3.9196649078378947,
    7: 4.067941763030685,
    14: 4.431945064252602,
    35: 4.449871418243051,
    9: 5.030418532753124,
    33: 6.157359727145053,
    4: 10.127682030108325,
    2: 23.629527447651384,
}

length_weights = {
    1: 0.7860357684290993,
    0: 0.831938095056652,
    3: 0.8358509920358522,
    2: 1.0827286247127685,
    7: 1.1440977637838259,
    15: 1.197249393757025,
    5: 1.2413911402067268,
    11: 1.935575513196481,
    9: 2.4774023671167322,
    4: 3.5105788402709495,
    13: 4.444900654383272,
    6: 5.6677847654729465,
    8: 9.305130565430844,
    10: 13.286630178615724,
    14: 15.812639716840536,
    12: 16.905740489130437,
}

def melody_model(validation_split=0.2, batch_size=32, epochs=1, nr_files=None, callbacks=False):
    if not force:

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

    del offset_sequences_o
    del length_sequences_o
    del pitch_sequences_o
    del next_pitches_o
    del next_lengths_o

    assert validation_split < 1 and validation_split >= 0

    random.shuffle(zipped_data)
    test_data = zipped_data[:int(len(zipped_data) * validation_split)]
    train_data = zipped_data[int(len(zipped_data) * validation_split):]

    del zipped_data

    model.fit_generator(generator=melody_data_generator(train_data, batch_size),
                        steps_per_epoch=len(train_data) // batch_size,
                        epochs=epochs, verbose=1, validation_data=melody_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=30, callbacks=callbacks)



if __name__ == '__main__':

    vs = 0.2
    bs = 10
    ep = 2
    nr_s = 10
    cb = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-f':
            force = True
            i += 1
        elif sys.argv[i] == '-vs':
            vs = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '-bs':
            bs = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '-ep':
            ep = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '-nr_s':
            if sys.argv[i + 1] == 'all':
                nr_s = None
            else:
                nr_s = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '-cb':
            cb = True
            i += 1
        else:
            raise ValueError("option not understood:", sys.argv[i])

    melody_model(vs, bs, ep, nr_s, cb)