import preprocessing.constants as c
from preprocessing.vanilla_part import VanillaPart
from preprocessing.vanilla_stream import VanillaStream


def get_max_values(probable_chords: dict) -> list:
    max_value = -1
    max_list = []

    for chord in probable_chords:
        if probable_chords[chord] > max_value:
            max_value = probable_chords[chord]
            max_list = [(max_value, chord)]
        elif probable_chords[chord] == max_value:
            max_list.append((max_value, chord))

    return max_list


def find_chords(note_stream: VanillaStream, melody_stream: VanillaStream) -> VanillaStream:
    # Todo: Issue 10
    # assert melody_stream.isSequence()

    chord_and_melody_stream = VanillaStream()

    note_stream_list = list(note_stream.flat.notes)
    melody_stream_list = list(melody_stream.flat.notes)

    last_needed_event = int(note_stream.highestTime) * 4

    melody_note_list = [None] * last_needed_event

    notes_per_melody_note_dict = {}

    for melody_note in melody_stream_list:
        start_idx = int(melody_note.offset * 4)
        end_idx = int((melody_note.offset + melody_note.quarterLength) * 4)
        melody_note_list[start_idx:end_idx] = [melody_note.id] * int(end_idx - start_idx)
        notes_per_melody_note_dict[melody_note.id] = []

    for note in note_stream_list:

        start_idx = int(note.offset * 4)
        end_idx = int((note.offset + note.quarterLength) * 4)
        melody_notes = set(melody_note_list[start_idx:end_idx])

        try:
            melody_notes.remove(None)
        except KeyError:
            pass

        for note_id in melody_notes:
            notes_per_melody_note_dict[note_id].append(note.pitch.ps)

    chord_and_melody_stream.insert(melody_stream.parts[0:])

    chord_part = VanillaPart()
    chord_part.id = "Chords"

    for note_id in notes_per_melody_note_dict:

        current_note = melody_stream.flat.getElementById(note_id)

        assert current_note is not None

        probable_chords = dict((elem, 0.0) for elem in c.chord_data["chord_to_notes"].keys())

        for pitch in notes_per_melody_note_dict[note_id]:

            str_pitch = str(int(pitch % 12))

            for temp_chord in c.chord_data["note_to_chords"][str_pitch]:
                probable_chords[temp_chord] += 1

        for chord in probable_chords:
            probable_chords[chord] /= len(c.chord_data["chord_to_notes"][chord])

        max_list = get_max_values(probable_chords)

        print(max_list)


def most_probable_chord(pitch_list):
    pass
