import os
import sys

import numpy as np
import random
import tensorflow as tf
import keras.callbacks as call_backs
from keras.backend import set_session
from keras.layers import Input, LSTM, Dense, concatenate, Masking, Dropout, Embedding
from keras.models import Model, load_model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

import settings.constants as c
import settings.constants_model as c_m
import settings.music_info_pb2 as music_info
from model.custom_callbacks import ModelCheckpointBatches, ModelCheckpoint, ReduceLREarlyStopping
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
    on_full_beat = []

    if nr_songs is None:
        nr_songs = len(all_data.songs)

    random.seed(42)
    all_songs = list(all_data.songs)
    random.shuffle(all_songs)
    random.seed()

    for song_data in all_songs[:nr_songs]:

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

            if np.sum(current_pitches) != 0:

                chord_sequences.append(current_chords)
                melody_sequences.append(current_pitches)
                start_sequences.append(current_starts)
                on_full_beat.append([i % 2, (i + 1) % 2])

                next_chords.append(chords[i])
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

def chord_model(validation_split=0.2, batch_size=32, epochs=1, nr_songs=None, callbacks=False, walltime=0):

    temp_save_path = os.path.join(c.project_folder, "data/tf_weights/weights_chord_final_saved_wall_time.hdf5")

    if not force:
        fit = input("Fit chord model? Y/n")
        if fit != 'Y':
            return

    chord_sequences, melody_sequences, start_sequences, on_full_beat, next_chords \
        = make_chord_data_from_file(nr_songs=nr_songs)

    ##########################################################################################
    ################# MODEL
    ##########################################################################################

    if 'REDO' in os.environ and os.environ['REDO'] == 'True':
        model = load_model(temp_save_path)
        initial_epoch = int(os.environ['EPOCH'])
        print("Model retraining starting in epoch %d" % initial_epoch)
    else:
        try:
            os.remove(os.path.join(c.project_folder, "data/info/cf/info.json"))
        except FileNotFoundError:
            pass

        print("Initial model building")
        initial_epoch = 0

        chord_input = Input(shape=(c_m.chord_sequence_length, 25), dtype='float32', name='chord_input')
        melody_input = Input(shape=(8 * 38,), dtype='float32', name='melody_input')
        start_input = Input(shape=(8,), dtype='float32', name='start_input')
        on_full_beat_input = Input(shape=(2,), dtype='float32', name='on_full_beat_input')

        concatenate_pre = concatenate([melody_input, start_input, on_full_beat_input], axis=-1)

        dense_pre = Dense(64, activation='relu', name='dense_pre')(concatenate_pre)

        dense_pre_dropout = Dropout(0.5)(dense_pre)

        masked_input = Masking(0.0)(chord_input)

        lstm = LSTM(256)(masked_input)

        dropout = Dropout(0.2)(lstm)

        concatenate_final = concatenate([dense_pre_dropout, dropout], axis=-1)

        dense_final = Dense(25, activation='softmax', name='dense_final')(concatenate_final)

        model = Model(inputs=[chord_input, melody_input, start_input, on_full_beat_input],
                      outputs=[dense_final])

        model.compile(loss={'dense_final': 'categorical_crossentropy'},
                      metrics=['accuracy'],
                      optimizer=Adam(lr=0.001))

        print(model.summary(90))

    ##########################################################################################
    ################# CALLBACKS
    ##########################################################################################

    if callbacks:
        terminate_on_nan = call_backs.TerminateOnNaN()

        filepath = os.path.join(c.project_folder, "data/tf_weights/cf/chord-weights-final-improvement-{epoch:02d}-"
                                                  "vl-{val_loss:.5}-vacc-{val_acc:.5}.hdf5")

        os.makedirs(os.path.split(filepath)[0], exist_ok=True)

        checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True,
                                                mode='min')

        batches_checkpoint = ModelCheckpointBatches(monitor='loss', period=200, walltime=walltime,
                                                    start_epoch=initial_epoch, temp_save_path=temp_save_path)

        early_stopping_lr = ReduceLREarlyStopping(file=os.path.join(c.project_folder, "data/info/cf/info.json"),
                                                  factor=0.8, patience_lr=20, min_lr=0.000008, patience_stop=50)

        os.makedirs(os.path.join(c.project_folder, "data/tensorboard_logs/cf"), exist_ok=True)
        tensorboard = call_backs.TensorBoard(log_dir=os.path.join(c.project_folder, "data/tensorboard_logs/cf"))

        callbacks = [terminate_on_nan, checkpoint, batches_checkpoint, early_stopping_lr, tensorboard]
    else:
        callbacks = []

    ##########################################################################################
    ################# DATA PREPARATION
    ##########################################################################################

    zipped_data = list(zip(chord_sequences, melody_sequences, start_sequences,
                           on_full_beat, next_chords))

    del chord_sequences
    del melody_sequences
    del start_sequences
    del on_full_beat
    del next_chords

    assert validation_split < 1 and validation_split >= 0

    test_data = zipped_data[:int(len(zipped_data) * validation_split)]
    train_data = zipped_data[int(len(zipped_data) * validation_split):]

    print("Number of data points in training data:", len(train_data))
    print("Number of data points in validaion data:", len(test_data))
    print("Batch size:", int(batch_size))
    print("Steps in an epoch:", int(len(train_data) // batch_size))

    del zipped_data

    ##########################################################################################
    ################# MODEL FITTING
    ##########################################################################################

    verbose = 1
    if force:
        verbose = 0

    model.fit_generator(generator=chord_data_generator(train_data, batch_size),
                        steps_per_epoch=len(train_data) // batch_size,
                        epochs=epochs, verbose=verbose, validation_data=chord_data_generator(test_data, batch_size),
                        validation_steps=len(test_data) // batch_size, max_queue_size=200,
                        callbacks=callbacks, class_weight=None,
                        initial_epoch=initial_epoch)

    if callbacks and walltime:
        if batches_checkpoint.reached_wall_time:
            from subprocess import call
            recallParameter = 'qsub -v REDO=True,EPOCH=' + str(
                batches_checkpoint.start_epoch) + ' final_chord_model.sge'
            call(recallParameter, shell=True)


if __name__ == '__main__':

    vs = 0.2
    bs = 32
    ep = 100
    nr_s = 3
    cb = True
    wall_time = 1000

    force=True

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