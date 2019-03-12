import music21 as m21

import settings.constants as c
from music_utils.vanilla_part import VanillaPart
from music_utils.vanilla_stream import VanillaStream


def stream_from_pb(pb_instance):
    """
    creates a VanillaStream from a protocol PieceOfMusic message,
    as specified in settings.music_info.proto
    :param pb_instance: the PieceOfMusic instance
    :return:
    """

    if not pb_instance.valid:
        return None

    full_stream = VanillaStream(filename=pb_instance.filepath)
    full_stream.key = pb_instance.key
    full_stream.key_correlation = pb_instance.key_correlation

    full_stream.insert(m21.meter.TimeSignature('4/4'))
    full_stream.insert(m21.tempo.MetronomeMark(number=120))

    for part in pb_instance.parts:

        temp_part = VanillaPart()
        temp_part.autoSort = False
        temp_part.partName = part.name
        temp_part.note_percentage = part.note_percentage
        temp_part.lyrics_percentage = part.lyrics_percentage

        for note in part.notes:

            if note.pitch < 0:
                temp_rest = m21.note.Rest()
                temp_rest.quarterLength = note.length
                temp_part.insert(note.offset, temp_rest)

            elif 0 <= note.pitch <= 128:
                temp_note = m21.note.Note()
                temp_note.quarterLength = note.length
                temp_note.pitch.ps = note.pitch
                temp_note.volume.velocity = note.volume
                temp_part.insert(note.offset, temp_note)

            else:
                raise ValueError("Pitch can't be higher than 128!")

        full_stream.insert(temp_part.sorted)

    return full_stream


if __name__ == "__main__":

    import settings.music_info_pb2 as mi

    with open(c.PROTOCOL_BUFFER_LOCATION, 'rb') as fp:
        music_protocol_buffer = mi.MusicList()
        music_protocol_buffer.ParseFromString(fp.read())

    counter = 0

    for pom in music_protocol_buffer.music_data:

        if counter == 10:
            break

        if pom.valid:
            stream = stream_from_pb(pom)

            if not stream:
                print("It didn't work")
                continue

            stream.show('midi')

            counter += 1
