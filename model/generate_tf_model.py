import os

import numpy as np

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
from tensorflow.python.keras.backend import set_session

from tensorflow._api.v1.keras.layers import Input, LSTM, Dense, concatenate, Masking
from tensorflow._api.v1.keras.models import Model
from tensorflow._api.v1.keras.optimizers import Adam
from tensorflow._api.v1.keras.preprocessing.sequence import pad_sequences

import model.make_tf_structure as make_tf

from tensorflow._api.v1.keras.utils import to_categorical

import settings.constants_model as c

config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
set_session(sess)  # set this TensorFlow session as the default session for Keras

pitch_input = Input(shape=(c.sequence_length, 37), dtype='float32', name='pitch_input')
length_input = Input(shape=(c.sequence_length, 16), dtype='float32', name='length_input')
offset_input = Input(shape=(c.sequence_length, 4), dtype='float32', name='offset_input')

concatenated_input = concatenate([pitch_input, length_input, offset_input], axis=-1)

masked_input = Masking(0.0)(concatenated_input)

lstm_layer = LSTM(512)(masked_input)

pitch_output = Dense(37, activation='softmax', name='pitch_output')(lstm_layer)
length_output = Dense(16, activation='softmax', name='length_output')(lstm_layer)

model = Model(inputs=[pitch_input, length_input, offset_input],
              outputs=[pitch_output, length_output])

weights_filename = "data/tf_weights/weights-improvement-tf-project-20-0.2772.hdf5 "
model.load_weights(weights_filename)

model.compile(loss={'pitch_output': 'categorical_crossentropy',
                    'length_output': 'categorical_crossentropy'},
              optimizer=Adam())

########################################################

for melody_nr in range(1):

    start_pitch = make_tf.pitch_to_int(60)
    start_length = make_tf.length_to_int(1.0)

    # print("Seed:")
    # print("\"" + ' '.join([str(int_to_char[value]) for value in pattern]) + "\"")

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    melody_string_list = [(60, 1.0, 0.0)]

    # for i in range(100):

    pitch_input_one_hot = to_categorical([start_pitch], num_classes=37)
    pitch_input_pad = pad_sequences([pitch_input_one_hot], maxlen=c.sequence_length,
                                    dtype='float32', padding='pre',
                                    truncating='post', value=0.0)

    length_input_one_hot = to_categorical([start_length], num_classes=16)
    length_input_pad = pad_sequences([length_input_one_hot], maxlen=c.sequence_length,
                                     dtype='float32', padding='pre',
                                     truncating='post', value=0.0)

    offset = 0.0
    offset_input_gen = make_tf.offset_to_binary_array(offset)
    offset_input_pad = pad_sequences([[offset_input_gen]], maxlen=c.sequence_length,
                                     dtype='float32', padding='pre',
                                     truncating='post', value=0.0)

    for i in range(100):
        pitch_pred, length_pred = model.predict([pitch_input_pad, length_input_pad, offset_input_pad], verbose=0)

        pitch_idx = np.random.choice(a=len(pitch_pred[0]), size=1, p=pitch_pred[0])[0]
        length_idx = np.random.choice(a=len(length_pred[0]), size=1, p=length_pred[0])[0]
        # length of last note
        offset = offset + melody_string_list[-1][1]

        melody_string_list.append((make_tf.int_to_pitch(pitch_idx),
                                   make_tf.int_to_length(length_idx),
                                   offset))

        pitch_one_hot = to_categorical([pitch_idx], num_classes=37)
        length_one_hot = to_categorical([length_idx], num_classes=16)
        offset_bool = make_tf.offset_to_binary_array(offset)
        offset_bool = np.reshape(offset_bool, (1, 4))

        pitch_input_res = np.reshape(pitch_input_pad, (30, 37))
        pitch_input_res = np.concatenate([pitch_input_res, pitch_one_hot], axis=0)
        pitch_input_res = pitch_input_res[1:]
        pitch_input_pad = np.reshape(pitch_input_res, (1, 30, 37))

        length_input_res = np.reshape(length_input_pad, (30, 16))
        length_input_res = np.concatenate([length_input_res, length_one_hot], axis=0)
        length_input_res = length_input_res[1:]
        length_input_pad = np.reshape(length_input_res, (1, 30, 16))

        offset_input_res = np.reshape(offset_input_pad, (30, 4))
        offset_input_res = np.concatenate([offset_input_res, offset_bool], axis=0)
        offset_input_res = offset_input_res[1:]
        offset_input_pad = np.reshape(offset_input_res, (1, 30, 4))

    from music_utils.vanilla_stream import VanillaStream
    import music21 as m21

    vs = VanillaStream()

    print(melody_string_list)

    for pitch, length, offset in melody_string_list:
        if pitch == 200:
            n = m21.note.Rest()
        else:
            n = m21.note.Note()
            n.pitch.ps = pitch
        n.quarterLength = length
        n.offset = offset
        vs.insert(n)

    vs.show('midi')

    # with open(melody_file_name + str(melody_nr), 'x') as fp:
    #     fp.write(' '.join(melody_string_list))

print("\nDone")
