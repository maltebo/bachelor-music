import music21 as m21

from preprocessing.vanilla_stream import VanillaStream


def find_chords(note_stream: VanillaStream, melody_stream: VanillaStream) -> VanillaStream:
    assert melody_stream.isSequence()

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


def make_chord_dict():
    import json

    maj = m21.chord.Chord(['C', 'E', 'G'])
    min = m21.chord.Chord(['C', 'E-', 'G'])
    dim = m21.chord.Chord(['C', 'E-', 'G-'])
    maj7 = m21.chord.Chord(['C', 'E', 'G', 'B'])
    min7 = m21.chord.Chord(['C', 'E-', 'G', 'B-'])

    base_note = m21.note.Note('C')

    chord_dict = {}

    for _ in range(12):
        chord_dict[base_note.name + " major"] = [p.ps % 12 for p in maj.pitches]
        maj = maj.transpose(1)
        chord_dict[base_note.name + " minor"] = [p.ps % 12 for p in min.pitches]
        min = min.transpose(1)
        chord_dict[base_note.name + " diminished"] = [p.ps % 12 for p in dim.pitches]
        dim = dim.transpose(1)
        chord_dict[base_note.name + " major 7"] = [p.ps % 12 for p in maj7.pitches]
        maj7 = maj7.transpose(1)
        chord_dict[base_note.name + " minor 7"] = [p.ps % 12 for p in min7.pitches]
        min7 = min7.transpose(1)

        base_note = base_note.transpose(1)

    note_dict = {}
    for i in range(12):
        note_dict[i] = []

    for key in chord_dict:
        for pitch in chord_dict[key]:
            note_dict[int(pitch)].append(key)

    full_dict = {
        "note_to_chords": note_dict,
        "chord_to_notes": chord_dict
    }

    with open("/home/malte/PycharmProjects/BachelorMusic/data/chord_data.json", 'x') as fp:
        fp.write(json.dumps(full_dict, indent=2))
