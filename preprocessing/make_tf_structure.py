import json

import preprocessing.constants as c
from preprocessing.vanilla_stream import VanillaStream


def make_tf_structure(vanilla_stream: VanillaStream):
    if len(vanilla_stream.parts) <= 1:
        return make_tf_melody(vanilla_stream)
    else:
        raise ValueError("Too many parts in the melody stream for current implementation")


def make_tf_melody(vanilla_stream: VanillaStream):
    melody_array = MelodyStructure(vanilla_stream).value_array

    melody_struct = {}
    melody_struct["PREP_SETTINGS"] = c.PREP_SETTINGS
    # Todo: make this algorithm variable!
    melody_struct["algorithm"] = "simple_skyline_algorithm"
    melody_struct["data"] = melody_array

    save_melody_struct(vanilla_stream.id, melody_struct)


def save_melody_struct(file_name: str, melody_struct: dict):
    c.melody_lock.acquire()
    try:
        with open(c.MELODY_FILE_PATH, 'r') as fp:
            current_melody_dict = json.load(fp)
            if file_name in current_melody_dict and melody_struct["PREP_SETTINGS"] == \
                    current_melody_dict[file_name]["PREP_SETTINGS"]:
                pass
            else:
                current_melody_dict[file_name] = melody_struct

        with open(c.MELODY_FILE_PATH, 'w') as fp:
            fp.write(json.dumps(current_melody_dict, indent=2))

    except FileNotFoundError:
        with open(c.MELODY_FILE_PATH, 'x') as fp:
            current_melody_dict = {file_name: melody_struct}
            fp.write(json.dumps(current_melody_dict, indent=2))

    finally:
        c.melody_lock.release()


class MelodyStructure:

    def __init__(self, vanilla_stream: VanillaStream):
        self.__value_array = []
        self.last_end = 0.0

        for note in vanilla_stream.flat.notes:
            self._insert(note.pitch.ps, note.offset, note.quarterLength)

    def _insert(self, pitch, start, length):

        if start == self.last_end:
            self.__value_array.append(values_to_int(pitch, length))
        elif start > self.last_end:
            pause_length = start - self.last_end
            while pause_length > 0.0:
                self.__value_array.append(values_to_int(0, min(4.0, pause_length)))
                pause_length -= min(4.0, pause_length)

            self.__value_array.append(values_to_int(pitch, length))
        else:
            raise ValueError("Something went wrong")

        self.last_end = start + length

    @property
    def value_array(self):
        return self.__value_array


def values_to_int(pitch: int, length: float) -> int:
    min_pitch = c.PREP_SETTINGS["MIN_PITCH"]
    max_pitch = c.PREP_SETTINGS["MAX_PITCH"]

    assert (min_pitch <= pitch <= max_pitch) or pitch == 0
    assert length % 0.25 == 0.0
    assert 0.0 < length <= 4.0

    # +2 for including both + break
    possible_pitches = c.PREP_SETTINGS["MAX_PITCH"] - min_pitch + 1

    pitch_int = pitch

    if pitch > 0:
        pitch_int = pitch - min_pitch + 1

    assert pitch_int <= possible_pitches

    return int(pitch_int + (possible_pitches + 1) * ((length - 0.25) * 4))


def int_to_values(value: int) -> (int, float):
    min_pitch = c.PREP_SETTINGS["MIN_PITCH"]
    max_pitch = c.PREP_SETTINGS["MAX_PITCH"]

    possible_pitches = max_pitch - min_pitch + 1

    assert (0 <= value <= possible_pitches + (possible_pitches + 1) * 16)

    # +2 for including both ends + break

    length = ((value // (possible_pitches + 1)) + 1) / 4
    pitch = value % (possible_pitches + 1)

    if pitch > 0:
        pitch += min_pitch - 1

    return pitch, length


print(values_to_int(84, 0.5))
print(int_to_values(73))
