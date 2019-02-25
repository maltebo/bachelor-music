from music21 import *
from preprocessing.vanilla_stream import VanillaStream
from preprocessing.vanilla_part import VanillaPart
from preprocessing.helper import round_to_quarter
import sys


def make_file_container(m21_file: stream.Score, file_name: str) -> VanillaStream:
    m21_stream = VanillaStream()

    m21_stream.id = file_name

    metronome_time_sig_stream = list(m21_file.flat.getElementsByClass(('MetronomeMark',
                                                                      'TimeSignature')))

    for elem in metronome_time_sig_stream:
        elem.offset = round_to_quarter(elem.offset)
        m21_stream.insert_local(elem)

    return m21_stream


def process_file(m21_file: stream.Score, m21_stream: VanillaStream):

    for part in list(m21_file.parts):

        delete = False

        for instr in part.getInstruments(recurse=True):
            if "drum" in instr.bestName().lower():
                m21_file.remove(part, recurse=True)
                delete = True
                break

        if delete:
            continue

        part.toSoundingPitch(inPlace=True)

        temp_part = VanillaPart()

        for elem in part.flat.getElementsByClass(('Note', 'Chord')):
            temp_part.insert_local(elem)

        temp_part.makeRests(fillGaps=True, inPlace=True)

        temp_part.stripTies(inPlace=True)

        m21_stream.insert(temp_part)


def transpose_key(mxl_file: stream.Score) -> bool:

    try:
        key = mxl_file.analyze('key')
    except:
        print(sys.exc_info())
        return False

    if key.mode != 'major' and key.mode != 'minor':
        return False

    if key.type == "major":
        interval_ = interval.Interval(key.tonic, pitch.Pitch('C'))
        mxl_file.transpose(interval_, inPlace=True)
    else:
        interval_ = interval.Interval(key.tonic, pitch.Pitch('A'))
        mxl_file.transpose(interval_, inPlace=True)
    return True


def check_valid_time_and_bpm(m21_stream: VanillaStream) -> bool:
    max_bpm = 140
    min_bpm = 100
    valid_time = "4_4"

    try:
        return (m21_stream.metronome_mark_max <= max_bpm and
                m21_stream.metronome_mark_min >= min_bpm and
                m21_stream.time_signature == valid_time)
    except TypeError:
        return False


def process_data(thread_id, file_name) -> VanillaStream:
    print("%s processing %s" % (thread_id, file_name))
    m21_file = converter.parse(file_name)

    m21_stream = make_file_container(m21_file, file_name)

    # valid = check_valid_time_and_bpm(m21_stream)
    #
    # if not valid:
    #     return None

    process_file(m21_file, m21_stream)

    transpose_key(m21_stream)

    return m21_stream


