import os
import numpy as np
import tensorflow as tf
from keras.backend import set_session
from keras.layers import Input, LSTM, Dense, concatenate, Masking
from keras.models import Model, load_model
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import settings.constants_model as c
import music_utils.simple_classes as simple
import model.converting as converter

def generate(filepath, num_songs=1, length_songs=200, save=False, show=True, input_notes=None):

    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    config.log_device_placement = False  # to log device placement (on which device the operation ran)
    # (nothing gets printed in Jupyter, only if you run it standalone)
    sess = tf.compat.v1.Session(config=config)
    set_session(sess)

    if input_notes is None:
        input_notes = [(72,1.0)]

    model = load_model(filepath)

    ########################################################

    for melody_nr in range(num_songs):

        note_list = simple.NoteList()
        start_pitches = []
        start_lengths = []
        for p, l in input_notes:
            start_pitches.append(converter.pitch_to_id[p])
            start_lengths.append(converter.quarter_length_to_id[l])
            if not note_list:
                note_list.append(simple.Note(offset=0.0,length=l,pitch=p))
            else:
                note_list.append(simple.Note(offset=note_list[-1].offset + note_list[-1].length,
                                             length=l, pitch=p))
        # print("Seed:")
        # print("\"" + ' '.join([str(int_to_char[value]) for value in pattern]) + "\"")

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        # for i in range(100):

        pitch_input_one_hot = to_categorical(start_pitches, num_classes=38)
        pitch_input_pad = pad_sequences([pitch_input_one_hot], maxlen=c.sequence_length,
                                        dtype='float32', padding='pre',
                                        truncating='post', value=0.0)

        length_input_one_hot = to_categorical(start_lengths, num_classes=16)
        length_input_pad = pad_sequences([length_input_one_hot], maxlen=c.sequence_length,
                                         dtype='float32', padding='pre',
                                         truncating='post', value=0.0)

        offset = 0.0
        if note_list:
            offset = note_list[-1].offset + note_list[-1].length
        offset_input_gen = np.array(converter.quarter_offset_to_binary_array(offset))

        for i in range(length_songs):

            offset_input_gen = np.reshape(offset_input_gen, newshape=(1,4))

            pitch_pred, length_pred = model.predict([pitch_input_pad, length_input_pad, offset_input_gen], verbose=0)

            pitch_idx = np.random.choice(a=len(pitch_pred[0]), size=1, p=pitch_pred[0])[0]
            length_idx = np.random.choice(a=len(length_pred[0]), size=1, p=length_pred[0])[0]
            # length of last note

            pitch = converter.id_to_pitch[pitch_idx]
            length = converter.id_to_quarter_length[length_idx]
            note_list.append(simple.Note(offset=offset, length=length, pitch=pitch))

            offset += length

            pitch_one_hot = to_categorical([pitch_idx], num_classes=38)
            length_one_hot = to_categorical([length_idx], num_classes=16)
            offset_binary = converter.quarter_offset_to_binary_array(offset)
            offset_input_gen = np.array(offset_binary)

            pitch_input_res = np.reshape(pitch_input_pad, (c.sequence_length, 38))
            pitch_input_res = np.concatenate([pitch_input_res, pitch_one_hot], axis=0)
            pitch_input_res = pitch_input_res[1:]
            pitch_input_pad = np.reshape(pitch_input_res, (1, c.sequence_length, 38))

            length_input_res = np.reshape(length_input_pad, (c.sequence_length, 16))
            length_input_res = np.concatenate([length_input_res, length_one_hot], axis=0)
            length_input_res = length_input_res[1:]
            length_input_pad = np.reshape(length_input_res, (1, c.sequence_length, 16))


        from music_utils.vanilla_stream import VanillaStream
        import music21 as m21

        print(note_list)

        stream = note_list.m21_stream

        if show:
            stream.show('midi')

        if save:
            raise ValueError("Function not available yet")

if __name__ == '__main__':
    generate(filepath="/home/malte/PycharmProjects/BachelorMusic/data/tf_weights/melody-weights-improvement-23.hdf5",
             length_songs=200, input_notes=[(72,1.0)])