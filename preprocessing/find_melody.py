from music21 import *
from copy import deepcopy
from sortedcontainers import SortedList
from preprocessing.vanilla_stream import VanillaStream


def get_highest_pitch_for_each_chord(chord_stream: stream.Stream):

    note_stream = VanillaStream()

    chord_list = list(chord_stream.flat.notes)

    for temp_chord in chord_list:
        temp_note = note.Note()
        temp_note.offset = temp_chord.offset
        temp_note.quarterLength = temp_chord.quarterLength
        temp_pitches = [p for p in temp_chord.pitches if 48.0 < p.ps <= 84.0]

        try:
            temp_note.pitch.ps, temp_note.pitch.groups, temp_pitch = max([(p.ps, p.groups, p) for p in temp_pitches])
            note_stream.insert(temp_note)
        except ValueError:
            pass

    return note_stream


def simple_skyline_algorithm(chord_stream: stream.Stream):

    current_note = None
    current_note_pitch = None
    current_end = -1
    melody_stream = VanillaStream()

    note_stream = get_highest_pitch_for_each_chord(chord_stream)

    for action_note in note_stream.flat.notes:

        action_pitch = action_note.pitch.ps

        if current_end <= action_note.offset:
            if current_note is not None:
                new_note = deepcopy(current_note)
                melody_stream.insert(new_note)
            current_note = action_note
            current_note_pitch = action_pitch
            current_end = action_note.offset + action_note.quarterLength

        elif action_pitch > current_note_pitch or (action_pitch == current_note_pitch and
                                                   action_note.offset + action_note.quarterLength > current_end):
            if action_note.offset - current_note.offset > 0:
                new_note = deepcopy(current_note)
                new_note.quarterLength = action_note.offset - new_note.offset
                melody_stream.insert(new_note)
            current_note = action_note
            current_note_pitch = action_pitch
            current_end = action_note.offset + action_note.quarterLength

    if current_note is not None:
        new_note = deepcopy(current_note)
        melody_stream.insert(new_note)

    # melody_stream.show()
    return melody_stream


# def skyline_algorithm(note_stream):
#     # note_stream.show()
#
#     melody_stream = stream.Stream()
#
#     action_list = []
#
#     for stream_note in note_stream.flat.notes:
#         action_list.append((stream_note.offset, "start", stream_note))
#         action_list.append((stream_note.offset + stream_note.quarterLength, "end", stream_note))
#
#     action_list.sort()
#
#     current_note = None
#     current_note_pitch = None
#     current_start = None
#     current_end = None
#
#     current_list = SortedList()
#     note_list = []
#
#     for offset, action, action_note in action_list:
#
#         if action == "start":
#
#             current_list.add((action_note.pitch.ps, -1 * action_note.quarterLength, action_note))
#
#             if current_start is None:
#
#                 current_note = action_note
#                 current_note_pitch = action_note.pitch.ps
#                 current_start = offset
#                 current_end = offset + current_note.quarterLength
#
#             else:
#
#                 if (action_note.pitch.ps > current_note_pitch or
#                         (action_note.pitch.ps == current_note_pitch and
#                          current_end < offset + action_note.quarterLength)):
#                     new_note = deepcopy(current_note)
#
#                     new_note.offset = current_start
#                     new_note.quarterLength = offset - current_start
#
#                     note_list.append(new_note)
#
#                     current_note = action_note
#                     current_note_pitch = action_note.pitch.ps
#                     current_start = offset
#                     current_end = offset + current_note.quarterLength
#
#         elif action == "end":
#
#             if current_start is None:
#                 raise ValueError("Note ends before it started!")
#
#             current_list.remove((action_note.pitch.ps, -1 * action_note.quarterLength, action_note))
#
#             if action_note == current_note:
#
#                 new_note = deepcopy(current_note)
#
#                 new_note.offset = current_start
#                 new_note.quarterLength = offset - current_start
#
#                 note_list.append(new_note)
#
#                 if current_list:
#
#                     current_note_pitch, new_duration, current_note = current_list[0]
#
#                     current_start = offset
#                     current_end = current_note.offset + current_note.quarterLength
#
#                 else:
#                     current_note = None
#                     current_start = None
#                     current_note_pitch = None
#                     current_end = None
#
#         else:
#             print("Error!")
#
#     for note in note_list:
#         if note.quarterLength > 0.0:
#             melody_stream.insert(note)
#
#     # melody_stream.show()
#     return melody_stream

