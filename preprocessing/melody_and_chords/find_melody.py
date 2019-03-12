from copy import deepcopy

import music21 as m21

import settings.constants as c
from m21_utils.vanilla_stream import VanillaStream


def simple_skyline_algorithm(note_stream: m21.stream.Stream):

    current_note = None
    current_note_pitch = None
    current_end = -1
    melody_stream = VanillaStream()
    melody_stream.id = note_stream.id

    for action_note in note_stream.flat.notes:

        action_pitch = action_note.pitch.ps

        if not (c.music_settings.min_pitch <= action_pitch <= c.music_settings.max_pitch):
            continue

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

    assert melody_stream.isSequence()

    melody_stream.makeMeasures(inPlace=True)
    # # not necessary, but nicer for looking at the notes
    melody_stream.makeAccidentals(inPlace=True)

    return melody_stream


# Todo: include volume information, lyrics information, maybe entropy

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

