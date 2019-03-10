import json
import sys

import numpy as np
import tensorflow as tf
from tensorflow.python.keras.backend import set_session

import preprocessing.constants as c

config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = True  # to log device placement (on which device the operation ran)
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
set_session(sess)  # set this TensorFlow session as the default session for Keras

with open(c.MELODY_FILE_PATH, 'r') as fp:
    melody_dict = json.load(fp)

full_melody = []
for key in melody_dict:
    full_melody.extend(melody_dict[key]["data"])

notes = sorted(list(set(full_melody)))
notes_to_int = dict((c, i) for i, c in enumerate(notes))

nr_notes = len(full_melody)
nr_vocab = len(notes)

print("Total note number:", nr_notes)
print("Total vocab:", nr_vocab)

seq_len = 12
dataX = []
dataY = []

for i in range(0, nr_notes - seq_len, 1):
    seq_in = full_melody[i:i + seq_len]
    seq_out = full_melody[i + seq_len]
    dataX.append([notes_to_int[note] for note in seq_in])
    dataY.append(notes_to_int[seq_out])

n_patterns = len(dataX)
print("Total patterns:", n_patterns)

X = np.reshape(dataX, (n_patterns, seq_len, 1))

X = X / float(nr_vocab)

y = tf.one_hot(indices=dataY, depth=nr_vocab)

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.LSTM(256, input_shape=(X.shape[1], X.shape[2])))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(y.shape[1], activation='softmax'))

filename = "weights-improvement-37-0.5823.hdf5"
model.load_weights(filename)
model.compile(loss='categorical_crossentropy', optimizer=tf.train.AdamOptimizer())

int_to_char = dict((i, c) for i, c in enumerate(notes))

start = np.random.randint(0, len(dataX) - 1)
pattern = dataX[start]

print("Seed:")
print("\"" + ' '.join([str(int_to_char[value]) for value in pattern]) + "\"")

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

for i in range(1000):
    x = np.reshape(pattern, (1, len(pattern), 1))
    x = x / float(nr_vocab)
    prediction = model.predict(x, verbose=0)
    index = np.argmax(prediction)
    result = int_to_char[index]
    seq_in = [int_to_char[value] for value in pattern]
    sys.stdout.write(str(result) + " ")
    pattern.append(index)
    pattern = pattern[1:len(pattern)]

print("\nDone")
