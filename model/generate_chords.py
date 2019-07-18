import numpy as np
import tensorflow as tf
from keras.backend import set_session
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import settings.constants_model as c
import music_utils.simple_classes as simple
import model.converting as converter
notes = list([[0.0, 0.25, 72, 120, 4294967296], [0.25, 0.25, 72, 120, 4294967296], [0.5, 0.25, 72, 120, 4294967296], [0.75, 0.25, 72, 120, 4294967296], [1.0, 0.5, 72, 120, 4294967296], [1.5, 0.75, 200, 120, 4294967296], [2.25, 0.25, 72, 120, 4294967296], [2.5, 0.5, 71, 120, 4294967296], [3.0, 0.5, 72, 120, 4294967296], [3.5, 0.5, 71, 120, 4294967296], [4.0, 0.5, 200, 120, 4294967296], [4.5, 0.25, 72, 120, 4294967296], [4.75, 0.25, 71, 120, 4294967296], [5.0, 0.25, 72, 120, 4294967296], [5.25, 0.25, 200, 120, 4294967296], [5.5, 0.5, 72, 120, 4294967296], [6.0, 0.5, 71, 120, 4294967296], [6.5, 0.5, 71, 120, 4294967296], [7.0, 0.25, 71, 120, 4294967296], [7.25, 0.25, 200, 120, 4294967296], [7.5, 0.5, 71, 120, 4294967296], [8.0, 2.0, 72, 120, 4294967296], [10.0, 0.25, 72, 120, 4294967296], [10.25, 0.25, 72, 120, 4294967296], [10.5, 0.25, 72, 120, 4294967296], [10.75, 0.25, 72, 120, 4294967296], [11.0, 1.0, 72, 120, 4294967296], [12.0, 0.75, 72, 120, 4294967296], [12.75, 0.25, 72, 120, 4294967296], [13.0, 0.25, 72, 120, 4294967296], [13.25, 0.25, 72, 120, 4294967296], [13.5, 0.5, 72, 120, 4294967296], [14.0, 1.0, 72, 120, 4294967296], [15.0, 1.0, 71, 120, 4294967296], [16.0, 1.0, 72, 120, 4294967296], [17.0, 1.0, 67, 120, 4294967296], [18.0, 0.25, 76, 120, 4294967296], [18.25, 0.25, 74, 120, 4294967296], [18.5, 0.5, 72, 120, 4294967296], [19.0, 0.5, 200, 120, 4294967296], [19.5, 0.5, 72, 120, 4294967296], [20.0, 2.0, 72, 120, 4294967296], [22.0, 0.5, 71, 120, 4294967296], [22.5, 0.5, 69, 120, 4294967296], [23.0, 0.5, 67, 120, 4294967296], [23.5, 0.5, 65, 120, 4294967296], [24.0, 1.5, 67, 120, 4294967296], [25.5, 1.25, 69, 120, 4294967296], [26.75, 0.5, 67, 120, 4294967296], [27.25, 0.5, 65, 120, 4294967296], [27.75, 0.5, 67, 120, 4294967296], [28.25, 0.25, 65, 120, 4294967296], [28.5, 1.5, 65, 120, 4294967296], [30.0, 1.5, 71, 120, 4294967296], [31.5, 0.25, 65, 120, 4294967296], [31.75, 2.25, 71, 120, 4294967296], [34.0, 0.5, 71, 120, 4294967296]])
note_list = simple.NoteList()
for elem in notes:
    note_list.append(simple.Note(*elem))

def generate(filepath, input_melody, save=False, show=True):

    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    config.log_device_placement = False
    sess = tf.compat.v1.Session(config=config)
    set_session(sess)

    last_chords = [converter.chord_to_id['None']]

    all_chords = []

    model = load_model(filepath)

    offset = 0.0

    note_array = [converter.pitch_to_id[200] for i in range(int(input_melody[-1].end()*4))]
    if len(note_array) % 8 != 0:
        note_array.extend([converter.pitch_to_id[200]]*(8-(len(note_array)%8)))
    assert len(note_array) % 8 == 0
    start_array = [0] * len(note_array)
    for note in input_melody:
        note_array[int(note.offset*4):int(note.end()*4)] = [converter.pitch_to_id[note.pitch]] * int(note.length*4)
        start_array[int(note.offset*4)] = 1

    for i in range(len(note_array)//8):
        current_notes = note_array[i*8:(i+1)*8]
        current_starts = np.asarray(start_array[i*8:(i+1)*8])

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        last_chords = last_chords[-c.chord_sequence_length:]

        chords = [to_categorical(chord, num_classes=25) for chord in last_chords]
        notes = [to_categorical(pitch, num_classes=38) for pitch in current_notes]
        chords = pad_sequences([chords], maxlen=c.chord_sequence_length, dtype='float32')

        chords  = np.reshape(chords, (1, c.chord_sequence_length, 25))

        melody = np.reshape(notes, (-1, 8 * 38))

        current_starts = np.reshape(current_starts, (1,8))
        full_beat = np.reshape(np.asarray([i%2, (i+1)%2]), (1,2))

        chord_pred = model.predict([chords, melody, current_starts, full_beat])

        new_chord = np.random.choice(len(chord_pred[0]), size=1, p=chord_pred[0])[0]

        last_chords.append(new_chord)
        all_chords.append(new_chord)

    return all_chords

if __name__ == '__main__':
    generate(filepath="/home/malte/PycharmProjects/BachelorMusic/data/tf_weights/cnw/chord-weights-nw-improvement-10-vl-1.3576-vacc-0.46875.hdf5",
             input_melody=note_list)