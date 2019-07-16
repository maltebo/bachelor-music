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
from model.custom_callbacks import ModelCheckpointBatches
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

def melody_model(validation_split=0.2, batch_size=32, epochs=1, nr_files=None, callbacks=False, walltime=0, temp=1.0):

    if not force:
        fit = input("Fit melody model? Y/n")
        if fit != 'Y':
            return

    offsets_o, length_sequences_o, pitch_sequences_o, next_pitches_o, next_lengths_o = \
        make_melody_data_from_file(nr_files=nr_files)

    ##########################################################################################
    ################# MODEL
    ##########################################################################################

    try:
        if os.environ['REDO'] == 'True':
            model = load_model(os.path.join(c.project_folder, "data/tf_weights/weights_saved_wall_time.hdf5"))
            initial_epoch = int(os.environ['EPOCH'])
        else:
            raise Exception()
    except:
        initial_epoch = 0

        pitch_input = Input(shape=(c_m.sequence_length, 38), dtype='float32', name='pitch_input')
        length_input = Input(shape=(c_m.sequence_length, 16), dtype='float32', name='length_input')
        offset_input = Input(shape=[4], dtype='float32', name='offset_input')

        concatenated_input = concatenate([pitch_input, length_input], axis=-1)

        masked_input = Masking(0.0)(concatenated_input)

        lstm_layer_1 = LSTM(512, input_shape=(50,54))(masked_input)

        dropout_1 = Dropout(rate=0.2)(lstm_layer_1)

        offset_input_n = Reshape([4])(offset_input)

        conc_out = concatenate([dropout_1, offset_input_n])

        pitch_output = Dense(38, activation='softmax', name='pitch_output')(conc_out)
        length_output = Dense(16, activation='softmax', name='length_output')(conc_out)

        model = Model(inputs=[pitch_input, length_input, offset_input],
                      outputs=[pitch_output, length_output])

        model.compile(loss={'pitch_output': 'categorical_crossentropy',
                            'length_output': 'categorical_crossentropy'},
                      metrics={'pitch_output': 'accuracy',
                               'length_output': 'accuracy'},
                      optimizer=Adam())

        print(model.summary(90))

    ##########################################################################################
    ################# CALLBACKS
    ##########################################################################################

    if callbacks:
        terminate_on_nan = call_backs.TerminateOnNaN()

        filepath = os.path.join(c.project_folder, "data/tf_weights/melody-weights-1LSTM-improvement-{epoch:02d}-"
                                                  "vl-{val_loss:0.5f}-pacc-{pitch_output_acc:0.5f}-lacc-{length_output_acc:0.5f}.hdf5")
        batch_filepath = os.path.join(c.project_folder, "data/tf_weights/melody-weights-improvement-batch.hdf5")
        os.makedirs(os.path.split(filepath)[0], exist_ok=True)

        checkpoint = call_backs.ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True,
                                                mode='min')

        batches_checkpoint = ModelCheckpointBatches(batch_filepath, monitor='loss', period=500, walltime=walltime)

        early_stopping = call_backs.EarlyStopping(monitor='loss', min_delta=0, patience=10,
                                          verbose=1, mode='auto', baseline=None)

        tensorboard = call_backs.TensorBoard(log_dir=os.path.join(c.project_folder, "data/tensorboard_logs"),
                                     update_freq=1000)

        reduce_lr = call_backs.ReduceLROnPlateau(monitor='loss', factor=0.2, verbose=1,
                                         patience=3, min_lr=0.000008)

        callbacks = [terminate_on_nan, checkpoint, batches_checkpoint, early_stopping, tensorboard, reduce_lr]
    else:
        callbacks = []

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
    print("Batch size:", batch_size)
    print("Steps in an epoch:", len(train_data) // batch_size)

    del zipped_data

    verbose = 1
    if force:
        verbose = 0

    model.fit_generator(generator=melody_data_generator(train_data, batch_size),
                        steps_per_epoch=len(train_data) // batch_size,
                        epochs=epochs, verbose=verbose, validation_data=melody_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=100,
                        callbacks=callbacks, class_weight=[pitch_weights, length_weights],
                        initial_epoch=initial_epoch)

    if callbacks and walltime:
        if batches_checkpoint.reached_wall_time:
            from subprocess import call
            recallParameter = 'qsub -v REDO=True,EPOCH=' + str(
                batches_checkpoint.last_epoch) + ' 1nw_melody_model.sge'
            call(recallParameter, shell=True)


if __name__ == '__main__':

    vs = 0.2
    bs = 32
    ep = 3
    nr_s = 5
    cb = True
    wall_time = 1550

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
        elif sys.argv[i] == '-wt':
            h,m,s = sys.argv[i+1].split(':')
            h = int(h)
            m = int(m)
            s = int(s)
            wall_time = s + 60*m + 3600*h
            i += 2
        else:
            raise ValueError("option not understood:", sys.argv[i])

    melody_model(vs, bs, ep, nr_s, cb, walltime=wall_time)