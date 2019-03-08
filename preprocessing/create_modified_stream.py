import traceback
from copy import deepcopy

import music21 as m21

import preprocessing.constants as c
from preprocessing.helper import FileNotFittingSettingsError
from preprocessing.helper import round_to_quarter
from preprocessing.vanilla_part import VanillaPart
from preprocessing.vanilla_stream import VanillaStream


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

    part: m21.stream.Part
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

        tie_list = []

        for elem in part.flat.getElementsByClass(('Note', 'Chord')):
            elem: m21.chord.Chord

            if elem.tie is None:
                temp_part.insert_local(elem)
                continue

            if elem.tie.type == 'start':
                tie_list.append([elem, elem.quarterLength, elem.offset + elem.quarterLength, pitch_set(elem)])
            elif elem.tie.type == 'continue':
                for tied_elem in list(tie_list):
                    if round(tied_elem[2], 4) < round(elem.offset, 4):
                        temp_part.insert_local(tied_elem[0], tied_elem[1])
                        tie_list.remove(tied_elem)
                    elif round(tied_elem[2], 4) == round(elem.offset, 4) and tied_elem[3] == pitch_set(elem):
                        tied_elem[1] += elem.quarterLength
                        tied_elem[2] += elem.quarterLength
                        break
            elif elem.tie.type == 'stop':
                for tied_elem in list(tie_list):
                    if round(tied_elem[2], 4) < round(elem.offset, 4):
                        temp_part.insert_local(tied_elem[0], tied_elem[1])
                        tie_list.remove(tied_elem)
                    elif round(tied_elem[2], 4) == round(elem.offset, 4) and tied_elem[3] == pitch_set(elem):
                        temp_part.insert_local(tied_elem[0], tied_elem[1] + elem.offset)
                        tie_list.remove(tied_elem)
                        break

        m21_stream.insert(temp_part)


def pitch_set(elem: m21.note.GeneralNote) -> set:
    return_set = set()
    for pitch in elem.pitches:
        return_set.add(pitch.ps)
    return return_set


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


def check_valid_time(m21_stream: VanillaStream):
    valid_time = c.PREP_SETTINGS["VALID_TIME"]

    if m21_stream.time_signature != valid_time:
        raise FileNotFittingSettingsError("Time doesnt't fit")


def check_valid_bpm(m21_stream: VanillaStream):
    if not (m21_stream.metronome_mark_max <= c.PREP_SETTINGS["MAX_BPM"] and
            m21_stream.metronome_mark_min >= c.PREP_SETTINGS["MIN_BPM"]):
        raise FileNotFittingSettingsError("Beats per minute don't fit")


def process_data(thread_id, file_name) -> VanillaStream:
    print("%s processing %s" % (thread_id, file_name))
    m21_file = m21.converter.parse(file_name)

    m21_stream = make_file_container(m21_file, file_name)

    check_valid_time(m21_stream)

    check_valid_bpm(m21_stream)

    process_file(m21_file, m21_stream)

    return m21_stream


def make_key_and_correlations(m21_stream: VanillaStream):
    if not transpose_key(m21_stream):
        raise ValueError("No transposition possible")

    stream_key = m21_stream.analyze('key')

    for p in list(m21_stream.parts):

        part_key = p.analyze('key')

        if stream_key.name != part_key.name:
            for k in part_key.alternateInterpretations:
                if k.name == stream_key.name:
                    part_key = k
                    break

        if stream_key.name != part_key.name:
            part_key = deepcopy(stream_key)
            part_key.correlationCoefficient = -1.0

        if part_key.correlationCoefficient < c.PREP_SETTINGS["DELETE_PART_THRESHOLD"]:
            m21_stream.remove(p, recurse=True)

        else:
            p.key = part_key.name
            p.key_correlation = part_key.correlationCoefficient

    if len(m21_stream.parts) == 0:
        m21_stream.key = "invalid"
        m21_stream.key_correlation = "invalid"
        return

    new_stream_key = m21_stream.analyze('key')
    if new_stream_key.name != stream_key.name or (new_stream_key.correlationCoefficient <
                                                  c.PREP_SETTINGS["DELETE_STREAM_THRESHOLD"]):
        m21_stream.key = "invalid"
        m21_stream.key_correlation = "invalid"
        return

    m21_stream.key = new_stream_key.name
    m21_stream.key_correlation = new_stream_key.correlationCoefficient
    return
