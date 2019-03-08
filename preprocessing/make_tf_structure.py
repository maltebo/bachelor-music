import preprocessing.constants as c
from preprocessing.vanilla_stream import VanillaStream


def make_tf_structure(vanilla_stream: VanillaStream):
    if len(vanilla_stream.parts) <= 1:
        return make_tf_melody(vanilla_stream)
    else:
        raise ValueError("Too many parts in the melody stream for current implementation")


def make_tf_melody(vanilla_stream: VanillaStream):
    melody_struct = MelodyStructure(vanilla_stream)

    for e in melody_struct.value_array:
        print(e)


class MelodyStructure:

    def __init__(self, vanilla_stream: VanillaStream):
        self.value_array = []
        self.last_end = 0.0

        for note in vanilla_stream.flat.notes:
            self._insert(note.pitch.ps, note.offset, note.quarterLength)

    def _insert(self, pitch, start, length):

        if start == self.last_end:
            self.value_array.append(values_to_int(pitch, length))
        elif start > self.last_end:
            pause_length = start - self.last_end
            while pause_length > 0.0:
                self.value_array.append(values_to_int(0, min(4.0, pause_length)))
                pause_length -= min(4.0, pause_length)

            self.value_array.append(values_to_int(pitch, length))
        else:
            raise ValueError("Something went wrong")

        self.last_end = start + length


def values_to_int(pitch: int, length: float) -> int:
    min_pitch = c.PREP_SETTINGS["MIN_PITCH"]
    max_pitch = c.PREP_SETTINGS["MAX_PITCH"]

    assert (min_pitch <= pitch <= max_pitch) or pitch == 0
    assert length % 0.25 == 0.0
    assert 0.0 < length <= 4.0

    # +2 for including both + break
    possible_pitches = c.PREP_SETTINGS["MAX_PITCH"] - min_pitch + 2

    pitch_int = pitch

    if pitch > 0:
        pitch_int = pitch - min_pitch + 1

    assert pitch_int <= possible_pitches

    return pitch_int + (possible_pitches + 1) * (length * 4)


def int_to_values(value: int) -> (int, float):
    min_pitch = c.PREP_SETTINGS["MIN_PITCH"]
    max_pitch = c.PREP_SETTINGS["MAX_PITCH"]

    possible_pitches = max_pitch - min_pitch + 2

    assert (0 <= value <= possible_pitches + (possible_pitches + 1) * 16)

    # +2 for including both ends + break

    length = ((value // (possible_pitches + 1)) + 1) / 4
    pitch = value % (possible_pitches + 1)

    if pitch > 0:
        pitch += min_pitch - 1

    return pitch, length
