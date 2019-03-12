import json

import converter.melody_converter as mc
import settings.constants as c
from m21_utils.vanilla_stream import VanillaStream
from preprocessing.helper import FileNotFittingSettingsError


def get_tf_structure(vanilla_stream: VanillaStream):
    if len(vanilla_stream.parts) <= 1:
        return make_tf_melody(vanilla_stream)
    else:
        raise ValueError("Too many parts in the melody stream for current implementation")


def make_tf_melody(vanilla_stream: VanillaStream):
    melody_array = MelodyStructure(vanilla_stream).value_array

    if not melody_array:
        raise FileNotFittingSettingsError("No melody found")

    melody_struct = {}
    # Todo: change this!
    melody_struct["PREP_SETTINGS"] = c.music_settings
    # Todo: make this algorithm variable!
    melody_struct["algorithm"] = "simple_skyline_algorithm"
    melody_struct["data"] = melody_array

    return melody_struct


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
        self.__melody_stream = None

        for note in vanilla_stream.flat.notes:
            self._insert(note.pitch.ps, note.offset, note.quarterLength)

    def _insert(self, pitch, start, length):

        if start == self.last_end:
            self.__value_array.append(mc.values_to_int(pitch, length))
        elif start > self.last_end:
            pause_length = start - self.last_end
            while pause_length > 0.0:
                self.__value_array.append(mc.values_to_int(0, min(4.0, pause_length)))
                pause_length -= min(4.0, pause_length)

            self.__value_array.append(mc.values_to_int(pitch, length))
        else:
            raise ValueError("Something went wrong")

        self.last_end = start + length

    @property
    def melody_stream(self):
        if self.__melody_stream:
            return self.__melody_stream

    @property
    def value_array(self):
        return self.__value_array
