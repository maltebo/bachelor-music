import numpy as np
import tensorflow as tf
from keras.backend import set_session
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import settings.constants_model as c
import music_utils.simple_classes as simple
import model.converting as converter
import model.generate_chords as gen_chords
import model.generate_melody as gen_melody
import music21 as m21

pitch_to_idx = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "E#": 5,
    "Fb": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "B#": 0,
    "Cb": 11
}


def make_chord_stream(chords):
    part = m21.stream.Part()
    for i, chord in enumerate(chords):
        chord = converter.id_to_chord[chord]
        if chord == 'None':
            continue
        sub = 0
        if chord.endswith('m'):
            sub = 1
        pitch_class = chord.replace('m', '')
        idx = pitch_to_idx[pitch_class]
        first = idx + 12*3
        third = first + 4 - sub
        fifth = first + 7
        offset = i*2
        n1 = m21.note.Note()
        n1.offset = offset
        n1.quarterLength = 0.5
        n1.pitch.ps = first
        n1.volume = 80
        n2 = m21.note.Note()
        n2.offset = offset + 0.5
        n2.quarterLength = 0.5
        n2.pitch.ps = third
        n2.volume = 70
        n3 = m21.note.Note()
        n3.offset = offset + 1.0
        n3.quarterLength = 0.5
        n3.pitch.ps = fifth
        n3.volume = 70
        n4 = m21.note.Note()
        n4.offset = offset + 1.5
        n4.quarterLength = 0.5
        n4.pitch.ps = third
        n4.volume = 70
        part.insert(n1)
        part.insert(n2)
        part.insert(n3)
        part.insert(n4)
    return part


def generate_random_song():

    vfl = [(200,3),(67,0.5),(67,0.5),(72,0.75),(71,0.75),(67,0.5),(67,1),(62,0.5),(62,0.5),(62,0.5),
                                              (64,0.5),(65,0.5),(64,1.5),]

    melody = gen_melody.generate("/home/malte/PycharmProjects/BachelorMusic/data/old_weights/melody-weights-1LSTMnw-improvement-88-vl-2.65555-vpacc-0.48237-vlacc-0.66568.hdf5",
                                 num_songs=1, show=False, length_songs=200,
                                 input_notes=None)[0]

    full_stream = m21.stream.Stream()

    full_stream.insert(melody.m21_stream)

    chords = gen_chords.generate("/home/malte/PycharmProjects/BachelorMusic/data/tf_weights/cnw/chord-weights-nw-improvement-51-vl-0.70464-vacc-0.77493.hdf5",
                                 input_melody=melody)

    part = make_chord_stream(chords)

    full_stream.insert(part)

    full_stream.show('midi')

if __name__ == '__main__':
    generate_random_song()