import numpy as np
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from tensorflow.python.keras.utils import to_categorical

import melody_converter as mc
import settings.constants_model as c_m
import settings.constants_preprocessing as c_p
import settings.music_info_pb2 as music_info
from music_utils.vanilla_stream import VanillaStream


# tf.enable_eager_execution()


def make_tf_data(settings=c_p.music_settings):
    pitches_input = []
    lengths_input = []
    offsets_input = []
    pitches_output = []
    lengths_output = []

    min_sequence_length = c_m.sequence_length + 1  # number of min beats per melody

    # while not c_m.melody_work_queue.empty():
    for i in range(500):

        melody = c_p.melody_work_queue.get()
        if not melody.endswith('_tf_skyline.melody_pb'):
            continue

        with open(melody, 'rb') as fp:
            melody_list = music_info.MelodyList()
            melody_list.ParseFromString(fp.read())

        for m in melody_list.melodies:
            if len(m.lengths) < min_sequence_length:
                continue

            pitches = [to_categorical([pitch_to_int(p, settings)], num_classes=38) for p in m.pitches]
            lengths = [to_categorical([length_to_int(l)], num_classes=16) for l in m.lengths]
            offsets = [offset_to_binary_array(o) for o in m.offsets]

            for time_step in range(len(m.lengths) - 2):
                pitches_input.append(pitches[max(0, time_step - c_m.sequence_length + 1): time_step + 1])
                lengths_input.append(lengths[max(0, time_step - c_m.sequence_length + 1): time_step + 1])
                offsets_input.append(offsets[max(0, time_step - c_m.sequence_length + 1): time_step + 1])

                pitches_output.append(pitches[time_step + 1])
                lengths_output.append(lengths[time_step + 1])

    pitches_input = pad_sequences(pitches_input, maxlen=c_m.sequence_length, dtype='float32')
    lengths_input = pad_sequences(lengths_input, maxlen=c_m.sequence_length, dtype='float32')
    offsets_input = pad_sequences(offsets_input, maxlen=c_m.sequence_length, dtype='float32')

    pitches_input = np.reshape(pitches_input, (-1, c_m.sequence_length, 38))
    lengths_input = np.reshape(lengths_input, (-1, c_m.sequence_length, 16))
    offsets_input = np.reshape(offsets_input, (-1, c_m.sequence_length, 4))

    pitches_output = np.reshape(pitches_output, (-1, 38))
    lengths_output = np.reshape(lengths_output, (-1, 16))

    return pitches_input, lengths_input, offsets_input, pitches_output, lengths_output


def pitch_to_int(pitch, settings=c_p.music_settings):
    assert (settings.min_pitch <= pitch <= settings.max_pitch) or pitch == 200
    return int((pitch - settings.min_pitch + 1) % (200 - settings.min_pitch + 1))


def int_to_pitch(int_pitch, settings=c_p.music_settings):
    assert int_pitch <= settings.max_pitch - settings.min_pitch + 1
    if int_pitch == 0:
        return 200
    return int_pitch + settings.min_pitch - 1


def length_to_int(length):
    assert 0.25 <= length <= 4.0
    return int(length * 4) - 1


def int_to_length(int_length):
    assert 0 <= int_length <= 15
    return (int_length + 1) / 4.0


def offset_to_binary_array(offset):
    return np.asarray([int(x) for x in format(int((offset % 4) * 4), '04b')[:]], dtype='float32')


# def generate(pitch_data: [[[int]]], length_data: [[[int]]], offset_data: [[[int]]]):
#
#     pitch_in = []
#     length_in = []
#     offset_in = []
#     pitch_out = []
#     length_out = []
#
#     for melody_pitches in pitch_data:
#
#         pitch_in.append([pitch_one_hot for pitch_one_hot in melody_pitches[:-1]])
#         pitch_out.append([pitch_one_hot for pitch_one_hot in melody_pitches[1:]])
#
#     for melody_lengths in length_data:
#
#         length_in.append([length_one_hot for length_one_hot in melody_lengths[:-1]])
#         length_out.append([length_one_hot for length_one_hot in melody_lengths[1:]])
#
#     for melody_offsets in offset_data:
#
#         offset_in.append([offset_binary for offset_binary in melody_offsets[:-1]])
#
#     return pitch_in, length_in, offset_in, pitch_out, length_out


class TfDataPoint:

    def __init__(self, real_pitch: int, real_length: float, real_offset: float, settings=c_p.music_settings):

        assert 0.0 < real_length <= 4.0

        assert settings.min_pitch <= real_pitch <= settings.max_pitch

        if real_pitch == 200:
            self.pitch = 0
        else:
            self.pitch = real_pitch - settings.min_pitch + 1

        assert 0 <= self.pitch <= settings.max_pitch - settings.min_pitch + 2

        self.offset = round(real_offset * 4)


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


if __name__ == '__main__':
    print(c_p.melody_work_queue.qsize())

    pitches_input, lengths_input, offsets_input, pitches_output, lengths_output = make_tf_data()

    print(len(lengths_output))
