import os
import random
import sys

import numpy as np
import time
import tensorflow as tf
import keras.callbacks as call_backs
from keras.backend import set_session
from keras.layers import Input, LSTM, Dense, concatenate, Masking
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

# for automated chord model training
force=False

def make_chord_data_from_file(nr_songs=None):
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

    if nr_songs is None:
        nr_songs = len(all_data.songs)

    for song_data in list(all_data.songs)[:nr_songs]:

        chords = list(song_data.chords)
        melody_list = np.zeros(8 * len(chords))
        start_list = np.zeros(8 * len(chords))

        for melody in song_data.melodies:
            # 200 is a break (coded as pitch 200), values range in between 48 and 84 - values from 0 to 37
            pitches = [converter.pitch_to_id[n] for n in melody.pitches]

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
    # 0,1 is full beat, 1,0 is half beat

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

chord_weights = {
    0: 0.7752530943367402,
    2: 0.7945722994766353,
    1: 0.8102732598537633,
    3: 0.9171759917393365,
    5: 0.9463738057655562,
    24: 1.2944299467950342,
    9: 1.3230306666666667,
    6: 1.3361606655755591,
    10: 1.63064956596252,
    8: 2.13950210151956,
    13: 2.4511525728679384,
    4: 3.3421170084439087,
    12: 3.4492708690190703,
    20: 3.585594409788868,
    7: 3.815427960057061,
    21: 4.207546259050684,
    16: 5.921191205425508,
    15: 6.365945592777383,
    19: 7.084587967305374,
    11: 9.201024311762602,
    23: 20.655275789473684,
    22: 24.45864092276831,
    18: 24.61422513881878,
    17: 26.85437879624517,
    14: 41.22519691780822,
}

def chord_model(validation_split=0.2, batch_size=32, epochs=1, nr_songs=None, callbacks=False, walltime=0):

    if not force:
        fit = input("Fit chord model? Y/n")
        if fit != 'Y':
            return

    chord_sequences, melody_sequences, start_sequences, on_full_beat, next_chords \
        = make_chord_data_from_file(nr_songs=nr_songs)

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
                      metrics=['accuracy'],
                      optimizer=Adam())

        print(model.summary(90))

    ##########################################################################################
    ################# CALLBACKS
    ##########################################################################################

    if callbacks:
        terminate_on_nan = call_backs.TerminateOnNaN()

        import datetime
        temp_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filepath = os.path.join(c.project_folder, "data/tf_weights/chords-weights-improvement-{t}.hdf5".format(t=temp_time))
        batch_filepath = filepath.replace('improvement', 'improvement-batched')
        os.makedirs(os.path.split(filepath)[0], exist_ok=True)
        checkpoint = call_backs.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, mode='min')

        early_stopping = call_backs.EarlyStopping(monitor='loss', min_delta=0, patience=5,
                                                  verbose=0, mode='auto', baseline=None)

        tensorboard = call_backs.TensorBoard(log_dir=os.path.join(c.project_folder, "data/tensorboard_logs"),
                                             #update_freq=5000
                                             )

        batches_checkpoint = ModelCheckpointBatches(batch_filepath, monitor='loss', period=2000, walltime=walltime)

        reduce_lr = call_backs.ReduceLROnPlateau(monitor='loss', factor=0.2,
                                                 patience=3, min_lr=0.001)

        callbacks = [terminate_on_nan, checkpoint, batches_checkpoint, early_stopping, tensorboard, reduce_lr]
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
                        epochs=epochs, verbose=0, validation_data=chord_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=100,
                        callbacks=callbacks, class_weight=chord_weights, initial_epoch=initial_epoch)

    if callbacks and walltime:
        if batches_checkpoint.reached_wall_time:
            from subprocess import call
            recallParameter = 'qsub -v REDO=True,EPOCH=' + str(
                batches_checkpoint.last_epoch) + ' chord_model.sge'
            call(recallParameter, shell=True)


if __name__ == '__main__':

    vs = 0.2
    bs = 10
    ep = 20
    nr_s = 20
    cb = True
    wall_time = 5000

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-f':
            force = True
            i += 1
        elif sys.argv[i] == '-vs':
            vs = float(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-bs':
            bs = float(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-ep':
            ep = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-nr_s':
            if sys.argv[i + 1] == 'all':
                nr_s = None
            else:
                nr_s = int(sys.argv[i+1])
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

    chord_model(vs, bs, ep, nr_s, cb, walltime=wall_time)