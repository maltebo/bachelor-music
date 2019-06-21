import json
from math import ceil
from math import floor

import music_utils.simple_classes as simple
import settings.constants as c

with open("/home/malte/PycharmProjects/BachelorMusic/web_scraping/chord_frequencies_and_transitions.json", 'r') as fp:
    chord_and_transition_dict = json.load(fp)

chord_to_idx = {
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

ROOT = 7 / 6
THIRD = 1
FIFTH = 5 / 6


def make_simple_chord_note_array(name: str):
    chord_note_array = [-1.0] * 12
    minor = name.endswith('m')
    if minor:
        name = name[:-1]
    root_index = chord_to_idx[name]
    chord_note_array[root_index] = ROOT
    chord_note_array[(root_index + 7) % 12] = FIFTH
    if minor:
        chord_note_array[(root_index + 3) % 12] = THIRD
    else:
        chord_note_array[(root_index + 4) % 12] = THIRD

    return chord_note_array


potential_chords = dict([(key, make_simple_chord_note_array(key)) for key in chord_and_transition_dict.keys()])


#
# chords_to_pitches = [
#     (0, 4, 7),
#     (2, 5, 9),
#     (4, 7, 11),
#     (5, 9, 0),
#     (7, 11, 2),
#     (9, 0, 4),
#     (11, 2, 5)
# ]
#
# pitches_to_chords = [
#     [0, 3, 5],
#     [],
#     [1, 4, 6],
#     [],
#     [0, 2, 5],
#     [1, 3, 6],
#     [],
#     [0, 2, 4],
#     [],
#     [1, 3, 5],
#     [],
#     [2, 4, 6]
# ]


def split_in_areas(song: simple.Song):
    '''
    splits a song in half measures
    :param song: song to be split
    :return:
    '''

    all_notes = song.notes(exclude_rests=True)

    last_note = max(all_notes, key=lambda x: x.offset + x.length)

    bucket_number = int(ceil((last_note.offset + last_note.length) / 2.0))

    if not bucket_number:
        return None

    full_split_song = [[] for _ in range(bucket_number)]

    # print(pitch_lists)
    #
    # current_start = floor(all_notes[0].offset / 2) * 2
    # pitch_list = []
    # next_pitch_list = []
    # next_next_pitch_list = []
    # chords = []
    # is_first_chord = True
    # last_chord = None

    for note in all_notes:

        assert note.length <= 4.0

        first_bucket = floor(note.offset / 2)
        last_bucket = (note.offset + note.length) / 2 - 1
        if (note.offset + note.length) % 2 > 0:
            last_bucket += 1

        i = first_bucket
        while i <= last_bucket:
            # pitch, length, offset in first bucket, starts_at?, volume
            full_split_song[i].append([note.pitch, note.length, note.offset - i * 2.0, note.volume])
            i += 1

    #     if start != current_start:
    #         chord = CMajChordStruct(pitch_list, last_chord, is_first_chord)
    #         most_probable = chord.get_most_probable()
    #         chords.append([current_start, chords_to_pitches[most_probable[0][1]]])
    #         is_first_chord = False
    #         current_start = start
    #         last_chord = most_probable[0][1]
    #         pitch_list = next_pitch_list
    #         next_pitch_list = next_next_pitch_list
    #         next_next_pitch_list = []
    #
    #     pitch_list.append([note.pitch, note.length, ((start + 2.0) - note.offset) / note.length, True, note.volume])
    #
    #     if note.end() > start + 2.0:
    #         next_pitch_list.append([note.pitch, note.length, (min(note.end(), start + 4.0) - (start + 2.0)) / note.length,
    #                            False, note.volume])
    #
    #         if note.end() > start + 4.0:
    #             next_next_pitch_list.append(
    #                 [note.pitch, note.length, (min(note.end(), start + 6.0) - (start + 4.0)) / note.length,
    #                  False, note.volume])
    #
    # return chords

    # print(full_split_song)

    return full_split_song


# class CMajChordStruct:
#     """
#     How to find the most probable chord:
#     given:
#     - list(note_pitch, total_length, length_percentage_in_chord_area, starts_in_area, volume)
#     - last chord
#     - if this chord is the first appearing
#
#     Calculation:
#     if this is the first appearing:
#     - add 10 points to the I chord (C maj in this case)
#     for each note:
#     - add total_length * length_percentage_in_chord_area * (volume/127) (* 2 if starts_in_area)
#         to chords containing the note
#     if no unambiguous maximum is found:
#     - add 3 points to the previous chord, 4 points to the descending third, 5 to the descending
#         fifth and 3 to the ascending second
#
#     return max
#     """
#     def __init__(self, pitch_list: [int, float, float, bool, int] = None, last_chord=None, is_first_chord: bool = False):
#
#         self.pitch_list = []
#         if pitch_list:
#             self.pitch_list.extend(pitch_list)
#
#         self.is_first_chord = is_first_chord
#         self.last_chord = last_chord
#
#         self.prob_array = [0] * len(chords_to_pitches)
#
#         self.calculate_most_probable()
#
#     def calculate_most_probable(self):
#
#         for pitch, total_length, length_percentage_in_chord_area, starts_in_area, volume in self.pitch_list:
#
#             for chord in pitches_to_chords[pitch % 12]:
#                 factor = 1
#                 if starts_in_area:
#                     factor = 2
#                 self.prob_array[chord] += total_length * length_percentage_in_chord_area * volume * factor
#
#     def get_most_probable(self):
#
#         return get_max_indexes(self.prob_array)


def get_max_indexes(probable_chords) -> list:
    max_value = -1
    max_list = []

    for i in range(len(probable_chords)):
        if probable_chords[i] > max_value:
            max_value = probable_chords[i]
            max_list = [(max_value, i)]
        elif probable_chords[i] == max_value:
            max_list.append((max_value, i))

    return max_list


def get_corresponding_chords(pitches_list):
    chord_list = ['None'] * len(pitches_list)
    # bass_list = ['None'] * len(pitches_list)

    note_prob = [None] * len(pitches_list)
    added_seventh = [0] * len(pitches_list)

    for i, note_list in enumerate(pitches_list):

        if i == 0:
            chord_list[i], note_prob[i] = get_chord(note_list, 'None', (i % 2))
            # if bass_note:
            #     bass_list[i] = bass_note
            # (i % 2) is first beat (0) or third beat (1)
        else:
            chord_list[i], note_prob[i] = get_chord(note_list, chord_list[i - 1], (i % 2))
            # if bass_note:
            #     bass_list[i] = bass_note

    for i, (prob, chord) in enumerate(zip(note_prob, chord_list)):
        print(chord, prob)

    return chord_list


def get_chord(note_list, previous_chord, metric_position):
    if not note_list:
        return previous_chord, [0] * 12

    if previous_chord == 'None':
        previous_chord = 'C'

    # bass_note = find_bass_note(note_list, metric_position)

    note_values = [0] * 12

    for note in note_list:
        pitch = note[0] % 12
        length_in_bucket = min(2.0, note[1] + note[2]) - max(0.0, note[2])
        factor = 1
        if note[2] == 0.0:
            factor = 2.0
        elif note[2] > 0.0:
            factor = 1.5
        note_values[pitch] += length_in_bucket * factor * note[3]

    probability = 0.0
    key = 'None'

    for chord in potential_chords:

        # if potential_chords[chord][bass_note % 12] > 0.0:

        transition_prob = 0.6
        if metric_position == 0:
            transition_prob = 0.5

        if chord != previous_chord:
            transition_prob = (1 - transition_prob) * chord_and_transition_dict[previous_chord][chord]

        chord_probability = sum([a * b for a, b in zip(potential_chords[chord], note_values)]) * transition_prob

        if chord_probability > probability:
            probability = chord_probability
            key = chord

    return key, note_values  # , bass_note


# def find_bass_note(note_list, metric_position):
#
#     # bass note should be played at least 1 beat long and either start in the beginning of this area or
#     # start in the beginning of the measure
#     potential_bass_notes = [note for note in note_list
#                             if (note[1] >= 1
#                                 and note[2] >= 0)
#                             or (note[1] >= 3.0
#                                 and note[2] == -2.0
#                                 and metric_position == 1)
#                             and (note[2] < 0.75)]
#
#     # print("Note List:", note_list)
#     # print("Potential bass notes:", potential_bass_notes)
#
#     if potential_bass_notes:
#         return min(potential_bass_notes, key=lambda x: x[0])[0]
#
#     potential_bass_notes = [note for note in note_list
#                             if note[1] >= 1.0
#                             and note[1] + note[2] >= 1.0]
#
#     if potential_bass_notes:
#         return min(potential_bass_notes, key=lambda x: x[0])[0]
#
#     return None


def make_simple_part_from_chords(chord_list, bass_list=None):
    chord_part = simple.NoteList()
    bass_part = simple.NoteList()

    for i, chord in enumerate(chord_list):
        if chord == 'None':
            continue
        chord_array = potential_chords[chord]
        root_idx = chord_array.index(ROOT)
        root = root_idx + 12 * 4
        third_idx = chord_array.index(THIRD)
        third = third_idx + 12 * 4
        if third < root:
            third += 12
        fifth_idx = chord_array.index(FIFTH)
        fifth = fifth_idx + 12 * 4
        if fifth < third:
            fifth += 12

        chord_part.append(simple.Note(i * 2, 2.0, root, 80))
        chord_part.append(simple.Note(i * 2, 2.0, third, 70))
        chord_part.append(simple.Note(i * 2, 2.0, fifth, 70))

    if bass_list:
        for i, bass_note in enumerate(bass_list):
            if bass_note == 'None':
                continue
            bass_part.extend(
                [simple.Note(i * 2, 2.0, bass_note + 12 * 3, 80), simple.Note(i * 2, 2.0, bass_note + 12 * 4, 80)])

    return chord_part, bass_part


if __name__ == "__main__":
    import os
    from settings.music_info_pb2 import VanillaStreamPB

    file_list = []

    for dirname, _, filenames in os.walk(c.MXL_DATA_FOLDER):

        for filename in filenames:
            if filename.endswith('.pb'):
                file_list.append(os.path.join(dirname, filename))

    for filename in file_list[10:11]:
        assert filename.endswith(".pb")

        proto_buffer_path = filename

        print(filename)

        with open(proto_buffer_path, 'rb') as fp:
            proto_buffer = VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        split_song = split_in_areas(simple_song)

        chords = get_corresponding_chords(split_song)

        print(chords)

        make_simple_part_from_chords(chords)
