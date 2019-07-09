import collections
import json
import os
import re

import settings.constants as c

with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'r') as fp:
    chord_dict = json.load(fp)

chord_to_idx = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "E#": 5,
    "Fb": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "B#": 0,
    "Cb": 11
}

idx_to_chord = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

complex_nr = 0
simple_nr = 0

simple_chord_list = []
complex_chord_list = []

simple_transitions = {}

progression_list = []

for elem in chord_dict:

    current_progression = ""

    curr_chords = chord_dict[elem]["chords"]

    if not curr_chords:
        continue

    tonality = chord_dict[elem]["tonality"]

    if tonality == "None":
        tonality = None

    if not tonality:

        if curr_chords[0] == curr_chords[-1]:

            res = re.fullmatch(r"([A-G][b#]{0,1}m{0,1})", curr_chords[0])
            if res:
                res = res.group(1)

            tonality = res

    if not tonality:
        continue

    start_chord = re.match(r"([A-G][b#]{0,1})", tonality).group(1)

    minor = tonality.endswith("m")

    if minor:
        continue

    # we only have major pieces at this point

    change_val = 0

    if start_chord != "C":
        change_val = chord_to_idx[start_chord]

    # we calculate the transpose value for the chords

    complex = False

    simple_song_chord_list = []
    song_chord_list = []

    for ch in curr_chords:

        ch = ch.replace("H", "B")
        ch = ch.replace("\\/", "/")

        root = re.match(r"([A-G][b#]{0,1})", ch)

        root_tone = root.group(1)

        rest = ch[root.end():]

        mode = rest.startswith("m") and not rest.startswith("maj")

        if mode:
            mode = "m"
            rest = rest[1:]
        else:
            mode = ""

        new_root = idx_to_chord[(chord_to_idx[root_tone] + 12 - change_val) % 12]

        if rest:
            halves = rest.split("/")
            if len(halves) == 2 and re.fullmatch(r"[A-G][b#]{0,1}", halves[1]):
                new_base = idx_to_chord[(chord_to_idx[halves[1]] + 12 - change_val) % 12]
                rest = '/'.join([halves[0], new_base])
            complex = True

        song_chord_list.append(new_root + mode + rest)

        if simple_song_chord_list:
            if simple_song_chord_list[-1] not in simple_transitions:
                simple_transitions[simple_song_chord_list[-1]] = {}

            if new_root + mode != simple_song_chord_list[-1]:

                if new_root + mode not in simple_transitions[simple_song_chord_list[-1]]:
                    simple_transitions[simple_song_chord_list[-1]][new_root + mode] = 1
                else:
                    simple_transitions[simple_song_chord_list[-1]][new_root + mode] += 1

        simple_song_chord_list.append(new_root + mode)

        if new_root + mode + rest == "C":
            if len(current_progression) > 1:
                progression_list.append(current_progression + ",C")
            current_progression = "C"

        elif len(current_progression) > 0:
            current_progression += "," + new_root + mode + rest

    if complex:
        complex_nr += 1
        complex_chord_list.extend(song_chord_list)
        simple_nr += 1
        simple_chord_list.extend(simple_song_chord_list)
    else:
        simple_nr += 1
        simple_chord_list.extend(song_chord_list)

complex_counts = collections.Counter(complex_chord_list)
simple_counts = collections.Counter(simple_chord_list)

# print("Complex Counts:", complex_counts)
# print("Simple Counts:", simple_counts)
#
# ##############################################################################
# # needed if we want to reduce the chord set
# ##############################################################################
# relevant_chords = [chord for chord, count in simple_counts.most_common(10)]
# for elem in dict(simple_transitions):
#     if elem not in relevant_chords:
#         del simple_transitions[elem]
#     else:
#         for inner_elem in dict(simple_transitions[elem]):
#             if inner_elem not in relevant_chords:
#                 del simple_transitions[elem][inner_elem]

chord_number = 0

for elem in simple_transitions:
    frequency = sum(simple_transitions[elem].values())
    chord_number += frequency
    for inner_elem in simple_transitions[elem]:
        simple_transitions[elem][inner_elem] /= frequency

    simple_transitions[elem]["frequency"] = frequency

for elem in simple_transitions:
    simple_transitions[elem]["frequency"] /= chord_number

# print("Progression Counter:")
# print(len(collections.Counter(progression_list)))
# print(collections.Counter([x for x in progression_list if len(x.split(",")) > 4]).most_common(100))

# normalize so that ech value is at least 0.01:
for elem in simple_transitions:
    simple_transitions[elem]["frequency"] = (simple_transitions[elem]["frequency"] + 0.07) / (
            1 + 0.07 * len(simple_transitions))
    for chord in idx_to_chord:
        if chord not in simple_transitions[elem]:
            simple_transitions[elem][chord] = 0.0
        if chord + 'm' not in simple_transitions[elem]:
            simple_transitions[elem][chord + 'm'] = 0.0
    for chord in simple_transitions[elem]:
        if chord == elem:
            assert simple_transitions[elem][chord] == 0
            del simple_transitions[elem][chord]
            break
    for temp_elem in simple_transitions[elem]:
        simple_transitions[elem][temp_elem] = (simple_transitions[elem][temp_elem] + 0.007) / (
                1 + 0.007 * (len(simple_transitions[elem]) - 1))

# print(json.dumps(simple_transitions,indent=2))

save = input("Save data and possibly overwrite existing data? Y/n")
if save == 'Y':
    with open(os.path.join(c.project_folder, "web_scraping/chord_frequencies_and_transitions_full.json"), 'w') as fp:
        fp.write(json.dumps(simple_transitions, indent=2))

plot = input("Do you want to plot the results? Y/n")
if plot != 'Y':
    import sys

    sys.exit()

import matplotlib.pylab as plt

simple_lists = sorted(zip(simple_counts.values(), simple_counts.keys()), reverse=True) # sorted by key, return a list of tuples

simple_x, simple_y = zip(*simple_lists)  # unpack a list of pairs into two tuples

plt.xlabel("most common chords in {} C major pieces not including complex chords".format(simple_nr))
plt.ylabel("total number of occurrences")
plt.xticks(rotation='vertical')
plt.plot(simple_y, simple_x)
# plt.plot(y, [xt / sum(x) for xt in x])
plt.show()


complex_lists = sorted(zip(complex_counts.values(), complex_counts.keys()), reverse=True) # sorted by key, return a list of tuples

complex_vals, complex_keys = zip(*complex_lists[:20]) # unpack a list of pairs into two tuples

plt.xlabel("20 most common chords in {} C major pieces including complex chords".format(complex_nr))
plt.ylabel("total number of occurrences")
plt.xticks(rotation='vertical')
plt.plot(complex_keys, complex_vals)
# plt.plot(y, [xt / sum(x) for xt in x])
plt.ticklabel_format()
plt.show()

# # pat = r"([A-G][b#]{0,1})([mM]{0,1})     (dim){0,1}     \d+{0,1}    (b\d){0,1}     (min){0,1}     (aug){0,1}   (maj\d+){0,1}     (sus\d*){0,1}     (add\d+){0,1}    "
#
# import numpy as np
#
# complex_transitions = np.zeros(shape=[len(complex_counts),len(complex_counts)], dtype=np.float64)
#
# key_dict = dict([(chord[1], count) for count, chord in enumerate(complex_lists)])
#
# for elem in chord_dict:
#
#     curr_chords = chord_dict[elem]["chords"]
#
#     if not curr_chords:
#         continue
#
#     tonality = chord_dict[elem]["tonality"]
#
#     if tonality == "None":
#         tonality = None
#
#     if not tonality:
#
#         if curr_chords[0] == curr_chords[-1]:
#
#             res = re.fullmatch(r"([A-G][b#]{0,1}m{0,1})", curr_chords[0])
#             if res:
#                 res = res.group(1)
#
#             tonality = res
#
#     if not tonality:
#         continue
#
#     start_chord = re.match(r"([A-G][b#]{0,1})", tonality).group(1)
#
#     minor = tonality.endswith("m")
#
#     if minor:
#         continue
#
#     # we only have major pieces at this point
#
#     change_val = 0
#
#     if start_chord != "C":
#         change_val = chord_to_idx[start_chord]
#
#     # we calculate the transpose value for the chords
#
#     complex = False
#
#     song_chord_list = []
#
#     for ch in curr_chords:
#
#         ch = ch.replace("H", "B")
#         ch = ch.replace("\\/", "/")
#
#         root = re.match(r"([A-G][b#]{0,1})", ch)
#
#         root_tone = root.group(1)
#
#         rest = ch[root.end():]
#
#         mode = rest.startswith("m") and not rest.startswith("maj")
#
#         if mode:
#             mode = "m"
#             rest = rest[1:]
#         else:
#             mode = ""
#
#         new_root = idx_to_chord[(chord_to_idx[root_tone] + 12 - change_val) % 12]
#
#         if rest:
#             halves = rest.split("/")
#             if len(halves) == 2 and re.fullmatch(r"[A-G][b#]{0,1}", halves[1]):
#                 new_base = idx_to_chord[(chord_to_idx[halves[1]] + 12 - change_val) % 12]
#                 rest = '/'.join([halves[0], new_base])
#             complex = True
#
#         song_chord_list.append(new_root + mode + rest)
#
#     if complex:
#         song_transitions = np.zeros(shape=complex_transitions.shape)
#         for i, j in zip(song_chord_list[:-1], song_chord_list[1:]):
#             song_transitions[key_dict[i]][key_dict[j]] += 1
#         song_transitions = song_transitions / np.sum(song_transitions)
#
#         complex_transitions += song_transitions
#     else:
#         pass
#
# complex_transitions_row_sums = np.sum(complex_transitions, axis=1)
# normalized_complex_transitions = complex_transitions / complex_transitions_row_sums[:, np.newaxis]
#
# # print(normalized_complex_transitions)
# # print(key_dict)
#
# with open("output.txt", 'w') as fp:
#     fp.write(json.dumps(normalized_complex_transitions.tolist(), indent=2))
