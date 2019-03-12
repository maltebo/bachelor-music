import traceback
from statistics import mean

import settings.constants as c
from m21_utils.vanilla_part import VanillaPart
from m21_utils.vanilla_stream import VanillaStream


def make_protocol_buffer_entry(m21_stream: VanillaStream, error_message):
    """
    makes a new protocol buffer entry to the protocol buffer specified in settings.constants,
    based on the m21_stream file
    :param m21_stream: Music piece that should be saved
    :param error_message: an optional message specifying why this file is not vaid for the current settings
    :return:
    """
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
        return

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

        add_notes_to_protocol_buffer(temp_part, p)


def add_notes_to_protocol_buffer(temp_part, part: VanillaPart):
    """
    adds all notes in a given stream to the given protocol buffer instance
    :param temp_part: a Part Protocol Buffer
    :param part: The part as a VanillaPart instance
    :return:
    """

    if temp_part.notes:
        return

    for elem in part.flat.getElementsByClass(('Note', 'Rest')):
        if elem.isNote:
            temp_part.notes.add(offset=elem.offset,
                                length=elem.quarterLength,
                                pitch=int(elem.pitch.ps),
                                volume=int(elem.volume.velocity))
        elif elem.isRest:
            temp_part.notes.add(offset=elem.offset,
                                length=elem.quarterLength,
                                pitch=-1)
        else:
            raise ValueError("Neither Rest nor Note")


def put_in_protocol_buffer(m21_stream: VanillaStream, error_message=None):
    """
    adds the information of the m21_stream file to the protocol buffer specified by the current settings.
    For further information, see settings.constants
    :param m21_stream: a VanillaStream instance of our musical piece
    :param error_message: an optional message saying why the stream is invalid with the current settings
    :return:
    """
    c.music_info_dict_lock.acquire()
    try:
        if proto_buffer_entry_exists(m21_stream.id):
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


def proto_buffer_entry_exists(filename: str) -> bool:
    """
    tests if the file is already in our database for the current settings
    :param filename: name of the (complete) filepath
    :return: True if the entry exists, False if it doesn't
    """

    return filename in c.existing_files
