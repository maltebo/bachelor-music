import model.converting as converter
import model.generate_chords as gen_chords
import model.generate_melody as gen_melody
import music21 as m21
import os
import settings.constants_model as c
import json
import random
import music_utils.simple_classes as simple

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

idx_to_pitch = {0: 'C', 1: 'C#', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}

def make_chord_stream_arpeggio(chords):
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
        n1.quarterLength = 2.0
        n1.pitch.ps = first
        n1.volume = 80

        n2 = m21.note.Note()
        n2.offset = offset
        n2.quarterLength = 2.0
        n2.pitch.ps = third
        n2.volume = 80

        n3 = m21.note.Note()
        n3.offset = offset
        n3.quarterLength = 2.0
        n3.pitch.ps = fifth
        n3.volume = 80

        part.insert(n1)
        part.insert(n2)
        part.insert(n3)
    return part

def make_chord_stream_slow(chords):
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
        n1.pitch.ps = first
        n1.offset = offset
        n1.quarterLength = 2.0
        n1.volume = 80
        n2 = m21.note.Note()
        n2.offset = offset + 1
        n2.quarterLength = 1.0
        n2.pitch.ps = third
        n2.volume = 70

        n3 = m21.note.Note()
        n3.offset = offset + 1
        n3.quarterLength = 1.0
        n3.pitch.ps = fifth
        n3.volume = 70
        part.insert(n1)
        part.insert(n2)
        part.insert(n3)
    return part

def generate_random_song(input_notes, length):

    vfl = [(200,3),(67,0.5),(67,0.5),(72,0.75),(71,0.75),(67,0.5),(67,1),(62,0.5),(62,0.5),(62,0.5),
                                              (64,0.5),(65,0.5),(64,1.5),]

    melody = gen_melody.generate("/home/malte/PycharmProjects/BachelorMusic/data/tf_weights/m3nw/melody-weights-3LSTMnw-improvement-472-vl-2.64893-vpacc-0.47701-vlacc-0.66466.hdf5",
                                 num_songs=1, show=False, length_songs=length,
                                 input_notes=input_notes)[0]

    full_stream = m21.stream.Stream()

    melody_stream = melody.m21_stream
    oboe = m21.instrument.Oboe()
    melody_stream.insert(0.0, oboe)

    full_stream.insert(melody_stream)

    chords = gen_chords.generate("/home/malte/PycharmProjects/BachelorMusic/data/tf_weights/cf/chord-weights-final-improvement-12-vl-0.69104-vacc-0.78332.hdf5",
                                 input_melody=melody)

    part = make_chord_stream_slow(chords)

    full_stream.insert(part)

    full_stream.makeNotation()

    filename = os.path.join(c.project_folder, "data/created_songs/song_length_{length}_input_{notes}_nr_".format(
        length=length, notes='_'.join(['-'.join([str(a) for a in o]) for o in input_notes[:5]])))

    final_name = ""

    for i in range(10000):
        final_name = filename + ("%03d" % i) + ".xml"
        if not os.path.exists(final_name):
            break

    print(final_name)

    os.makedirs(os.path.join(c.project_folder, "data/created_songs"), exist_ok=True)
    full_stream.write('musicxml', fp=final_name)

    data = {'melody': melody, 'chords': chords}
    with open(final_name.replace('xml','json'), 'w') as fp:
        json.dump(data, fp)

def show_midi(melody, chords):
    full_stream = m21.stream.Stream()

    melody_stream = melody.m21_stream
    oboe = m21.instrument.Oboe()
    melody_stream.insert(0.0, oboe)
    full_stream.insert(melody_stream)

    part = make_chord_stream_slow(chords)
    full_stream.insert(part)
    full_stream.makeNotation()

    full_stream.show('midi')

def list_to_note_list(list):
    out = simple.NoteList()
    for elem in list:
        n = simple.Note(elem[0], elem[1], elem[2], elem[3], elem[4])
        out.append(n)
    out.sort()
    return out

if __name__ == '__main__':

    # input_notes = [(200, 3)]
    # length = 100
    # for i in range(5):
    #     generate_random_song(input_notes, length)
    #
    # input_notes = [(60, 2)]
    # length = 100
    # for i in range(5):
    #     generate_random_song(input_notes, length)
    #
    # input_notes = [(72, 0.5)]
    # length = 100
    # for i in range(5):
    #     generate_random_song(input_notes, length)

    # for i in range(5):
    #     songs = list(c.all_data.songs)
    #     rand_song = songs[random.randrange(len(songs))]
    #     melodies = list(rand_song.melodies)
    #     rand_melody = melodies[random.randrange(len(melodies))]
    #
    #     first_offset = (rand_melody.offsets[0] % 12) / 4
    #     input_notes = []
    #     if first_offset:
    #         input_notes = [(200, first_offset)]
    #
    #     for p, o, l in list(zip(rand_melody.pitches, rand_melody.offsets, rand_melody.lengths))[:10]:
    #         input_notes.append([p, l/4])
    #
    #     length = 100
    #     generate_random_song(input_notes, length)

    for root,_,files in os.walk(os.path.join(c.project_folder, "data/created_songs")):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r') as fp:
                    data = json.loads(fp.read())
                melody = data['melody']
                chords = data['chords']

                melody = list_to_note_list(melody)

                show_midi(melody, chords)

                break