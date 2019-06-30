import re
from copy import deepcopy
from statistics import mean, stdev

import music_utils.simple_classes as simple
import settings.constants as c


def simple_skyline_algorithm_from_simple(song_or_part_or_parts_list,
                                         split: bool, max_rest: float = 4.0,
                                         min_melody_length: float = 16.0) -> [(float, simple.NoteList)]:
    '''
    creates melodies by applying a simple skyline algorithm
    :param song_or_part_or_parts_list: the notes file(s)
    :param split: if the melodies should be split
    :param max_rest: applicable only if split is true, max rest in a melody (without splitting)
    :param min_melody_length: minimal length of a melody, in quarter beats
    :return: a NoteList with the melody
    '''

    if type(song_or_part_or_parts_list) == simple.NoteList:
        notes = deepcopy(song_or_part_or_parts_list)

    elif type(song_or_part_or_parts_list) == simple.Part or \
            type(song_or_part_or_parts_list) == simple.Song:
        notes = song_or_part_or_parts_list.notes()

    elif type(song_or_part_or_parts_list) == list:
        notes = simple.NoteList()
        for part_or_song in song_or_part_or_parts_list:
            assert type(part_or_song) == simple.Part or type(part_or_song) == simple.Song or \
                   type(part_or_song) == simple.NoteList

            if type(part_or_song) == simple.NoteList:
                notes.extend(deepcopy(part_or_song))
            else:
                notes.extend(part_or_song.notes())

        notes.sort()

    else:
        raise ValueError("Type {t} doesn't fit, must be either simple.Part, simple.Song,"
                         "simple.NoteList or a list with the above!".format(t=type(song_or_part_or_parts_list)))

    assert type(notes) == simple.NoteList

    current_note = None
    current_end = -1

    melody = simple.NoteList()

    for note in notes:
        pitch = note.pitch

        # just allow pitches in the specified range
        # also immediately removes rests, which have per definition a pitch of 200
        # this is because protocol buffers have problems handling negative ints efficiently
        if not (c.music_settings.min_pitch <= pitch <= c.music_settings.max_pitch):
            continue

        # no jumps down greater than an octave!
        if current_note:
            if current_note.pitch - pitch > 12:
                continue

        if current_end <= note.offset:
            if current_note is not None:
                melody.append(current_note)
            current_note = note
            current_end = note.end()

        elif pitch > current_note.pitch or (note.offset > current_note.offset and
                                            note.part == current_note.part):
            if note.offset - current_note.offset > 0:
                current_note.length = note.offset - current_note.offset
                melody.append(current_note)
            current_note = note
            current_end = note.end()

    if current_note is not None:
        melody.append(current_note)

    assert is_sequence(melody)

    if not split:
        return [(0.0, melody)]

    return make_full_sub_melodies(melody, max_rest=max_rest,
                                  min_melody_length=min_melody_length)


# def tf_skyline(song: simple.Song, split: bool,
#                max_rest: float = 4.0, min_melody_length: float = 16.0) -> [(float, simple.NoteList)]:
#     '''
#     deprecated "advanced" skyline algorithm that won't be used in the future
#     :param song:
#     :param split:
#     :param max_rest:
#     :param min_melody_length:
#     :return:
#     '''
#     parts = []
#     average_volumes = []
#     average_pitches = []
#     all_notes = []
#
#     for part in song.parts:
#         temp_part_notes = simple_skyline_algorithm_from_simple(part, split=False)[0][1]
#         if len(temp_part_notes) > 0:
#             parts.append(simple_skyline_algorithm_from_simple(part, split=False)[0][1])
#
#     for i, part in enumerate(parts):
#         assert is_sequence(part)
#         part: simple.NoteList
#         average_volumes.append(mean([note.volume for note in part]))
#         average_pitches.append(mean([note.pitch for note in part]))
#         all_notes.extend(part)
#
#     # for calculating variance, at least 2 notes are needed. melody_length//4 is a
#     # lower bound for the least smallest amount of notes
#     if len(all_notes) < max(2, int(min_melody_length // 4)):
#         return None
#
#     probable_melody_parts = []
#
#     mean_volume = mean([n.volume for n in all_notes])
#     stdev_volume = stdev([n.volume for n in all_notes])
#     mean_pitch = mean([n.pitch for n in all_notes])
#     stdev_pitch = stdev([n.pitch for n in all_notes])
#
#     for avg_vol, avg_pitch, part in zip(average_volumes, average_pitches, parts):
#         if avg_vol >= mean_volume - stdev_volume:
#             probable_melody_parts.append(part)
#         elif avg_pitch >= mean_pitch - stdev_pitch:
#             probable_melody_parts.append(part)
#
#     result = simple_skyline_algorithm_from_simple(probable_melody_parts, split,
#                                                   max_rest, min_melody_length)
#
#     return result


def skyline_advanced(song: simple.Song, split: bool,
                     max_rest: float = 4.0, min_melody_length: float = 16.0):
    '''
    advanced skyline algorithm with extra features - disregarding low volume + low notes parts, etc.
    :param song: Song for which melody should be found
    :param split: should the melodies be split
    :param max_rest: rest length at which melodies are split
    :param min_melody_length: minimal melody length in quarter beats
    :return:
    '''
    parts = []
    average_volumes = []
    average_pitches = []
    lyrics_percentages = []
    all_notes = []

    for simple_part in song.parts:
        # calculate normal skyline algorithm for each part separately
        parts.append(simple_skyline_algorithm_from_simple(simple_part, split=False)[0][1])
        lyrics_percentages.append(simple_part.lyrics_percentage)

    longest_subsequences_length = {}
    longest_subsequences_notes = {}
    full_number_and_length = {}

    # for each part, calculate mean volume and pitch
    for i, note_list_part in enumerate(parts):
        assert (is_sequence(note_list_part))
        note_list_part: simple.NoteList
        if len(note_list_part) > 0:
            average_volumes.append(mean([note.volume for note in note_list_part]))
            average_pitches.append(mean([note.pitch for note in note_list_part]))
            assert (note_list_part[0].part == i)
            all_notes.extend(note_list_part)
        else:
            average_volumes.append(0.0)
            average_pitches.append(0.0)
        longest_subsequences_length[i] = 0.0
        longest_subsequences_notes[i] = 0
        full_number_and_length[i] = [0, 0.0]

    if len(all_notes) < 10:
        return False, None

    probable_melody_parts = []
    # save lyrics parts
    lyrics_parts = [part for part, lyrics in zip(parts, lyrics_percentages) if lyrics > 0.4]

    if not lyrics_parts:
        all_names = []
        for part in song.parts:
            part_name = part.name.lower()
            # backup / back vocals, vocal oohs, vocal aahs, harmony vocal, bckngvocal
            if "vocal" in part_name and not (
                    "back" in part_name or "ooh" in part_name or "aah" in part_name or "harmon" in part_name or "bckng" in part_name
                    or "vocalist" in part_name):
                # print(piece.filepath, part.name, "\n")
                all_names.append(part)
        if len(all_names) >= 1:
            for elem in list(all_names):
                if "lead" in elem.name.lower():
                    all_names = [elem]
                    break
                elif re.findall("[2-9]", elem.name.lower()):
                    all_names.remove(elem)
                    continue
                elif "1" in elem.name.lower():
                    all_names = [elem]
                    break

        lyrics_parts.extend([simple_skyline_algorithm_from_simple(elem, split=False)[0][1] for elem in all_names])

    if lyrics_parts:
        probable_melody_parts = lyrics_parts
    else:
        mean_volume = mean([n.volume for n in all_notes])
        stdev_volume = stdev([n.volume for n in all_notes])
        mean_pitch = mean([n.pitch for n in all_notes])
        stdev_pitch = stdev([n.pitch for n in all_notes])

        # throw out all very low volume and low note parts
        for avg_vol, avg_pitch, part in zip(average_volumes, average_pitches, parts):
            if avg_vol > mean_volume - stdev_volume:
                probable_melody_parts.append(part)
            elif avg_pitch > mean_pitch - stdev_pitch:
                probable_melody_parts.append(part)

    # parts in probable_melody_parts are now considered to be the ones most likely containing the piece's melody

    if lyrics_parts:
        if len(lyrics_parts) == 1:
            if not split:
                return True, [(0.0, lyrics_parts[0])]
            return True, make_full_sub_melodies(lyrics_parts[0], max_rest=max_rest,
                                                min_melody_length=min_melody_length)
        else:
            results = []
            for lyrics_part in lyrics_parts:
                if not split:
                    results.append((0.0, lyrics_part))
                else:
                    try:
                        results.extend(make_full_sub_melodies(lyrics_part, max_rest=max_rest,
                                                          min_melody_length=min_melody_length))
                    except TypeError:
                        print("Problem with file", song.name)
            if results:
                return True, results
            else:
                return False, None

    # if there are no lyrics parts, we'll find our result manually

    first_result = simple_skyline_algorithm_from_simple(probable_melody_parts, split=False)[0][1]

    current_subsequence_length = [0, 0.0]
    current_subsequence_notes = [0, 0]
    for note in first_result:
        note: simple.Note
        full_number_and_length[note.part][0] += 1
        full_number_and_length[note.part][1] += note.length
        if note.part == current_subsequence_length[0]:
            current_subsequence_length[1] += note.length
            current_subsequence_notes[1] += 1
        else:
            if longest_subsequences_length[current_subsequence_length[0]] < current_subsequence_length[1]:
                longest_subsequences_length[current_subsequence_length[0]] = current_subsequence_length[1]
            if longest_subsequences_notes[current_subsequence_notes[0]] < current_subsequence_notes[1]:
                longest_subsequences_notes[current_subsequence_notes[0]] = current_subsequence_notes[1]

            current_subsequence_length = [note.part, note.length]
            current_subsequence_notes = [note.part, 1]

    percentage_wanted = 0.95
    n: simple.Note
    note_length_needed = sum([n.length for n in first_result]) * percentage_wanted
    temp_length_list = [(full_number_and_length[key][1], key) for key in full_number_and_length]
    temp_length_list.sort(reverse=True)
    note_length = 0.0
    # only keep parts that together make up >= 95% of the notes
    for part_note_number, part_id in temp_length_list:
        if note_length > note_length_needed:
            if parts[part_id] in probable_melody_parts:
                probable_melody_parts.remove(parts[part_id])
        note_length += part_note_number

    # remove parts with short subsequences in melody
    for i, part in enumerate(parts):
        if part in probable_melody_parts:
            if longest_subsequences_length[i] < 4.0:
                probable_melody_parts.remove(part)
            elif longest_subsequences_notes[i] < 4:
                probable_melody_parts.remove(part)

    all_notes = simple.NoteList()
    for part in probable_melody_parts:
        all_notes.extend(part)

    all_notes.sort()

    # todo
    # print([i[0][-1] for i in probable_melody_parts])

    check = False
    current_result = simple_skyline_algorithm_from_simple(all_notes, split=False)[0][1]

    while not check:
        subsequences = "".join(
            [str(int(n1.part == n2.part)) for n1, n2 in zip(current_result[:-1], current_result[1:])])

        invalid_areas = re.finditer("00", subsequences)
        check = True
        # print(subsequences)

        # delete consequent notes coming from different parts
        for i in invalid_areas:
            check = False
            elem = current_result[i.span()[0] + 1]
            elem: simple.Note
            remove_element = [x for x in all_notes if x.offset == elem.offset
                              and elem.volume == x.volume
                              and x.pitch == elem.pitch
                              and x.part == elem.part]
            all_notes.remove(remove_element[0])

        # delete sequences of length two of one part
        if check:
            invalid_areas = re.finditer("010", subsequences)
            for i in invalid_areas:
                check = False
                elems = current_result[i.span()[0] + 1: i.span()[1]]
                assert len(elems) == 2
                for elem in elems:
                    remove_element = [x for x in all_notes if x.offset == elem.offset
                                      and elem.volume == x.volume
                                      and x.pitch == elem.pitch
                                      and x.part == elem.part]
                    all_notes.remove(remove_element[0])

        # delete sequences of length three of one part
        if check:
            invalid_areas = re.finditer("0110", subsequences)
            for i in invalid_areas:
                check = False
                elems = current_result[i.span()[0] + 1: i.span()[1]]
                assert len(elems) == 3
                for elem in elems:
                    remove_element = [x for x in all_notes if x.offset == elem.offset
                                      and elem.volume == x.volume
                                      and x.pitch == elem.pitch
                                      and x.part == elem.part]
                    all_notes.remove(remove_element[0])

        current_result = simple_skyline_algorithm_from_simple(all_notes, split=False)[0][1]

    if not split:
        return False, [(0.0, current_result)]

    return False, make_full_sub_melodies(current_result, max_rest=max_rest,
                                         min_melody_length=min_melody_length)


def is_sequence(notes: simple.NoteList):
    return all([first.end() <= second.offset for first, second in zip(notes[:-1], notes[1:])])


def make_full_sub_melodies(melody: simple.NoteList, max_rest: float, min_melody_length: float) \
        -> [(float, simple.NoteList)]:
    if not melody:
        return None
    melodies = split_melody(melody, max_rest, min_melody_length)
    full_melodies = []
    for m in melodies:
        m_breaks = make_breaks_and_start(m)
        if m_breaks:
            full_melodies.append(make_breaks_and_start(m))

    return full_melodies


def split_melody(melody: simple.NoteList, max_rest: float, min_melody_length: float):
    if not melody:
        return None

    split_indexes = [0]
    split_indexes.extend([i + 1
                          for i, (n1, n2)
                          in enumerate(zip(melody[:-1], melody[1:]))
                          if n2.offset > n1.end() + max_rest])
    split_indexes.append(len(melody))

    # splits the melody at breaks that take more than max_rest beats
    melodies = [simple.NoteList(melody[i1:i2])
                for i1, i2
                in zip(split_indexes[:-1], split_indexes[1:])
                if melody[i1].end() + min_melody_length <= melody[i2 - 1].offset]
    # the melodies should be at least min_melody_length beats long!

    return melodies


def make_breaks_and_start(melody: simple.NoteList) -> (float, simple.NoteList):
    """
    given a note list, returns a new note list with the rests before and after the melody starts deleted,
    and rests inserted at places where they belong
    :param melody: the NoteList specifying the melody
    :return: a new NoteList
    """
    start = melody[0].offset
    first_measure_start = (start // 4) * 4

    copied_melody = deepcopy(melody)
    for note in copied_melody:
        note.offset -= first_measure_start

    full_list = simple.NoteList()

    if copied_melody[0].offset > 0.0:
        full_list.append(simple.Note(offset=0.0,
                                     length=copied_melody[0].offset,
                                     pitch=200,
                                     volume=0,
                                     part=copied_melody[0].part))

    full_list.append(copied_melody[0])

    for note in copied_melody[1:]:
        if note.offset > full_list[-1].end():
            full_list.append(simple.Note(offset=full_list[-1].end(),
                                         length=note.offset - full_list[-1].end(),
                                         pitch=200,
                                         volume=0,
                                         part=full_list[-1].part))

        full_list.append(note)
    if full_list:
        return first_measure_start, full_list
    else:
        return None


if __name__ == '__main__':

    import os
    from settings.music_info_pb2 import VanillaStreamPB
    import google.protobuf.json_format as json_format
    from random import shuffle

    file_list = []

    for dirname, _, filenames in os.walk(c.MXL_DATA_FOLDER):

        for filename in filenames:
            if filename.endswith('.pb'):
                file_list.append(os.path.join(dirname, filename))
                pass

    # file_list.append((os.path.join(c_m.project_folder, "data/MXL/lmd_matched_mxl/D/B/E/TRDBEBI128F1495CAB/03eb725d73e98dd52dd026fe8c31e531.pb")))
    # file_list.append(os.path.join(c_m.project_folder, "data/MXL/lmd_matched_mxl/C/Q/D/TRCQDMP128F42483E0/143ee97082008e4f8781979fe2e42d76.pb"))

    shuffle(file_list)

    for filename in file_list:

        assert filename.endswith(".pb")

        proto_buffer_path = filename

        print(filename)

        with open(proto_buffer_path, 'rb') as fp:
            proto_buffer = VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        # print(simple_song)

        lyrics, full_melody = skyline_advanced(simple_song, split=False)

        if not lyrics:
            print("\nNo lyrics found!\n")
            # continue
        else:
            print("\nLyrics found!\n")
        # print([note.part for note in melody])

        if not full_melody:
            print("No melody found")
            print(json_format.MessageToJson(proto_buffer.info))
            # simple_song.m21_stream().show('text')
            #
            # # full_stream = stream_from_pb(proto_buffer)
            # simple_melody = simple_skyline_algorithm_from_simple(simple_song, split=False)[0][1]
            # # print(json_format.MessageToJson(proto_buffer.info))
            #
            # tf_melody = tf_skyline(simple_song, split=False)[0][1]
            #
            # if not simple_melody or not tf_melody:
            #     break
            #
            # all_melodies_song = simple.Song(list_of_parts_or_note_lists=[simple_melody,
            #                                                              tf_melody])
            # all_melodies_song.m21_stream().show('midi')
            #
            # full_melodies = make_full_sub_melodies(tf_melody, 4.0, 16.0)

        else:
            # pass
            # break
            # full_stream = stream_from_pb(proto_buffer)
            # simple_melody = simple_skyline_algorithm_from_simple(simple_song, split=False)[0][1]
            # # print(json_format.MessageToJson(proto_buffer.info))
            #
            # tf_melody = tf_skyline(simple_song, split=False)[0][1]

            # all_melodies_song.m21_stream().show('midi')

            # full_melodies = make_full_sub_melodies(tf_melody, max_rest=4.0, min_melody_length=16.0)

            # print("Full melodies:")
            #
            # [print(m) for m in full_melodies]

            from preprocessing.melody_and_chords import find_chords

            areas = find_chords.split_in_areas(simple_song)

            prob_chords = find_chords.get_corresponding_chords(areas)

            simple_chord_part, bass_chord_part = find_chords.make_simple_part_from_chords(prob_chords)

            full_song = simple.Song(list_of_parts_or_note_lists=[full_melody[0][1], simple_chord_part])

            # full_song.m21_stream().show('text')
            full_song.m21_stream().show('midi')

            break
