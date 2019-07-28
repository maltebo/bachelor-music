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
    # print("FREQUENCY",frequency)
    chord_number += frequency
    for inner_elem in simple_transitions[elem]:
        simple_transitions[elem][inner_elem] /= frequency

    simple_transitions[elem]["frequency"] = frequency

for elem in simple_transitions:
    simple_transitions[elem]["frequency"] /= chord_number

# print("Progression Counter:")
# cc = collections.Counter(progression_list)
# print(len(cc))
# print(collections.Counter([x for x in progression_list]).most_common(100))
#
# lengths = [len(x.split(',')) for x in progression_list]
# long_sequences = [len(x.split(',')) for x in progression_list if len(x.split(',')) > 20]
#
# print(collections.Counter([x for x in progression_list if len(x.split(',')) > 20]).most_common(10))
#
# print(len(long_sequences) / len(lengths))


# import matplotlib.pyplot as plt
#
# # import matplotlib as mpl
# # mpl.use("pgf")
# # pgf_with_rc_fonts = {
# #     "font.serif": ['cmr10'],                   # use latex default serif font
# #     "pgf.preamble": [
# #              "\\usepackage{musicography}",
# #              ]
# # }
# # mpl.rcParams.update(pgf_with_rc_fonts)
#
# plt.figure(figsize=(4,3))
# plt.hist(lengths, bins=max(lengths)-1)
# plt.xlabel("Lengths of chord progressions")
# plt.ylabel("Occurences in data")
# plt.tight_layout()
# # plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chord_progression_lengths.pdf')
# # plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chord_progression_lengths.pgf')
# plt.show()

# normalize so that each value is at least 0.05:
for elem in idx_to_chord:
    simple_transitions[elem]["frequency"] = (simple_transitions[elem]["frequency"] + 0.007) / (
            1 + 0.007 * (len(idx_to_chord)-1))
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

save = input("Save data and possibly overwrite existing data? Y/n")
if save == 'Y':
    with open(os.path.join(c.project_folder, "web_scraping/chord_frequencies_and_transitions_full.json"), 'w') as fp:
        fp.write(json.dumps(simple_transitions, indent=2))
