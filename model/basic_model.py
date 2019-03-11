import json

import numpy as np
import tensorflow as tf

import preprocessing.constants as c

tf.enable_eager_execution()

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

filename = "/home/malte/PycharmProjects/BachelorMusic/weights-improvement-50-0.3534.hdf5"
model.load_weights(filename)
model.compile(loss='categorical_crossentropy', optimizer=tf.train.AdamOptimizer())

filepath = "weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')

callbacks_list = [checkpoint]

model.fit(X, y, epochs=50, batch_size=256, callbacks=callbacks_list, validation_split=0.2)
