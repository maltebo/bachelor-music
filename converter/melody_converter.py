import os

import music21 as m21

import settings.constants as c
from m21_utils.vanilla_stream import VanillaStream


def values_to_int(pitch: int, length: float) -> int:
    min_pitch = c.music_settings.min_pitch
    max_pitch = c.music_settings.max_pitch

    assert (min_pitch <= pitch <= max_pitch) or pitch == 0
    assert length % 0.25 == 0.0
    assert 0.0 < length <= 4.0

    # +2 for including both + break
    possible_pitches = c.music_settings.max_pitch - min_pitch + 1

    pitch_int = pitch

    if pitch > 0:
        pitch_int = pitch - min_pitch + 1

    assert pitch_int <= possible_pitches

    return int(pitch_int + (possible_pitches + 1) * ((length - 0.25) * 4))


def int_to_values(value: int) -> (int, float):
    min_pitch = c.music_settings.min_pitch
    max_pitch = c.music_settings.max_pitch

    possible_pitches = max_pitch - min_pitch + 1

    assert (0 <= value <= possible_pitches + (possible_pitches + 1) * 16)

    # +2 for including both ends + break

    length = ((value // (possible_pitches + 1)) + 1) / 4
    pitch = value % (possible_pitches + 1)

    if pitch > 0:
        pitch += min_pitch - 1

    return pitch, length


def int_to_note(value: int) -> m21.note.Note:
    pitch, length = int_to_values(value)
    if pitch:
        note = m21.note.Note()
        note.pitch.ps = pitch
    else:
        note = m21.note.Rest()

    note.quarterLength = length

    return note


def file_to_m21_stream(filename) -> VanillaStream:
    with open(filename, 'r') as fp:
        melody_raw = ' '.join(fp.readlines())
        single_ints = melody_raw.split()

    melody_stream = VanillaStream(filename)
    offset = 0
    m_mark = m21.tempo.MetronomeMark(number=120)
    melody_stream.insert(offset, m_mark)
    for elem in single_ints:
        n = int_to_note(int(elem))
        melody_stream.insert(offset, n)
        offset += n.quarterLength

    return melody_stream


if __name__ == "__main__":
    for dirpath, dirnames, filenames in os.walk("/home/malte/PycharmProjects/BachelorMusic/data/generated_melodies"):
        for filename in filenames:
            melody_stream = file_to_m21_stream(os.path.join(dirpath, filename))
            melody_stream.show('midi')
