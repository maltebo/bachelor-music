import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.layers import Input, LSTM, Dense, concatenate, Masking
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import Adam

config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = True  # to log device placement (on which device the operation ran)
# (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
set_session(sess)

import settings.constants_model as c
import old.make_tf_structure as tf_struct

pitch_in, length_in, offset_in, pitch_out, length_out = tf_struct.make_tf_data()

pitch_input = Input(shape=(c.sequence_length, 38), dtype='float32', name='pitch_input')
length_input = Input(shape=(c.sequence_length, 16), dtype='float32', name='length_input')
offset_input = Input(shape=(c.sequence_length, 4), dtype='float32', name='offset_input')

concatenated_input = concatenate([pitch_input, length_input, offset_input], axis=-1)

masked_input = Masking(0.0)(concatenated_input)

lstm_layer = LSTM(512)(masked_input)

pitch_output = Dense(38, activation='softmax', name='pitch_output')(lstm_layer)
length_output = Dense(16, activation='softmax', name='length_output')(lstm_layer)

model = Model(inputs=[pitch_input, length_input, offset_input],
              outputs=[pitch_output, length_output])

old_weights = "data/tf_weights/weights-improvement-tf-project-20-0.2772.hdf5"
# model.load_weights(old_weights)

model.compile(loss={'pitch_output': 'categorical_crossentropy',
                    'length_output': 'categorical_crossentropy'},
              optimizer=Adam())

print(model.summary(90))

filepath = "data/tf_weights/weights-improvement-tf-project-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')

callbacks_list = [checkpoint]

model.fit([pitch_in, length_in, offset_in], [pitch_out, length_out],
          epochs=50, batch_size=32, callbacks=callbacks_list, validation_split=0.2)
