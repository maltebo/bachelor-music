import music21 as m21
from preprocessing.vanilla_stream import VanillaStream
from preprocessing.vanilla_part import VanillaPart
from preprocessing.helper import round_to_quarter
import traceback


def make_file_container(m21_file: m21.stream.Score, file_name: str) -> VanillaStream:
    m21_stream = VanillaStream()

    m21_stream.id = file_name

    metronome_time_sig_stream = list(m21_file.flat.getElementsByClass(('MetronomeMark',
                                                                      'TimeSignature')))

    for elem in metronome_time_sig_stream:
        elem.offset = round_to_quarter(elem.offset)
        m21_stream.insert_local(elem)

    return m21_stream


def process_file(m21_file: m21.stream.Score, m21_stream: VanillaStream):

    part_name_list = []
    number = 2

    for part in list(m21_file.parts):

        delete = False

        for instr in part.getInstruments(recurse=True):
            if instr.midiChannel == 9:
                delete = True
                break
            if "drum" in instr.bestName().lower():
                delete = True
                break

        if delete:
            continue

        part.toSoundingPitch(inPlace=True)

        temp_part = VanillaPart()

        if part.partName in part_name_list:
            temp_part.partName = part.partName + "_" + str(number)
            number += 1
        else:
            part_name_list.append(part.partName)
            temp_part.partName = part.partName

        for elem in part.flat.getElementsByClass(('Note', 'Chord')):
            temp_part.insert_local(elem)

        temp_part.makeRests(fillGaps=True, inPlace=True)

        temp_part.stripTies(inPlace=True)

        m21_stream.insert(temp_part)


def transpose_key(mxl_file: m21.stream.Score) -> bool:

    try:
        key = mxl_file.analyze('key')
    except:
        traceback.print_exc()
        return False

    if key.mode != 'major' and key.mode != 'minor':
        return False

    if key.type == "major":
        interval_ = m21.interval.Interval(key.tonic, m21.pitch.Pitch('C'))
        mxl_file.transpose(interval_, inPlace=True)
    else:
        interval_ = m21.interval.Interval(key.tonic, m21.pitch.Pitch('A'))
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
    m21_file = m21.converter.parse(file_name)

    m21_stream = make_file_container(m21_file, file_name)

    # valid = check_valid_time_and_bpm(m21_stream)
    #
    # if not valid:
    #     return None

    process_file(m21_file, m21_stream)

    transpose_key(m21_stream)

    return m21_stream


