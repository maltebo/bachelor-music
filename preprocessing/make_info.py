import traceback
from statistics import mean

import settings.constants as c
from preprocessing.vanilla_stream import VanillaStream


def make_protocol_buffer_entry(m21_stream: VanillaStream, error_message):
    c.music_protocol_buffer.counter = c.music_protocol_buffer.counter + 1
    music_file = c.music_protocol_buffer.music_data.add(filepath=m21_stream.id, valid=m21_stream.valid)
    if m21_stream.time_signature:
        music_file.time_signature = m21_stream.time_signature
    if m21_stream.min_metronome:
        music_file.min_metronome = int(m21_stream.min_metronome)
    if m21_stream.max_metronome:
        music_file.max_metronome = int(m21_stream.max_metronome)
    if m21_stream.key:
        music_file.key = m21_stream.key
        music_file.key_correlation = m21_stream.key_correlation
    if error_message:
        music_file.error_message = str(error_message)

    for p in m21_stream.parts:

        temp_part = music_file.parts.add(name=p.partName)
        temp_part.average_pitch = mean(p.pitch_list)
        temp_part.average_volume = mean(p.volume_list)
        if p.key:
            temp_part.key = p.key
            temp_part.key_correlation = p.key_correlation

        if p.total_notes_or_chords:
            temp_part.note_percentage = p.note_number / p.total_notes_or_chords
            temp_part.lyrics_percentage = p.lyrics_number / p.total_notes_or_chords
        else:
            temp_part.note_percentage = 0.0
            temp_part.lyrics_percentage = 0.0


def put_in_protocol_buffer(m21_stream: VanillaStream, error_message=None):
    c.music_info_dict_lock.acquire()
    try:
        if valid_entry_exists(m21_stream.id):
            c.music_info_dict_lock.release()
            return

        make_protocol_buffer_entry(m21_stream, error_message)
        c.existing_files[m21_stream.id] = m21_stream.valid

        if c.music_protocol_buffer.counter >= 10:
            print("write protocol buffer")
            with open(c.PROTOCOL_BUFFER_LOCATION, 'wb') as fp:
                fp.write(c.music_protocol_buffer.SerializeToString())
            c.music_protocol_buffer.counter = 0
        c.music_info_dict_lock.release()

    except:
        traceback.print_exc()
        c.music_info_dict_lock.release()


def valid_entry_exists(filename: str) -> bool:
    """
    tests if the file is already in our database for the current settings
    :param filename: name of the (complete) filepath
    :return: True if the entry exists, False if it doesn't
    """

    return filename in c.existing_files.keys()
