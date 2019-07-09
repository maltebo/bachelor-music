import json
import os
import re
import traceback

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

absolute_songs = 0
total_songs = 0
tonality_specified = 0
no_tonality_specified = 0
no_tonality_songs = 0
minor_songs = 0
major_songs = 0

simple_chord_list = []
simple_chord_dict = {}
complex_chord_list = []
complex_chord_dict = {}

for elem in chord_dict:

    absolute_songs += 1

    curr_chords = chord_dict[elem]["chords"]

    if not curr_chords:
        continue

    total_songs += 1

    tonality = chord_dict[elem]["tonality"]

    if tonality == "None":
        tonality = None

    if not tonality:

        no_tonality_specified += 1
        if curr_chords[0] == curr_chords[-1]:

            res = re.fullmatch(r"([A-G][b#]{0,1}m{0,1})", curr_chords[0])
            if res:
                res = res.group(1)

            tonality = res

    else:
        tonality_specified += 1

    if not tonality:
        no_tonality_songs += 1
        continue

    start_chord = re.match(r"([A-G][b#]{0,1})", tonality).group(1)

    minor = tonality.endswith("m")

    if minor:
        minor_songs += 1
        continue

    # we only have major pieces at this point

    major_songs += 1
    change_val = 0

    if start_chord != "C":
        change_val = chord_to_idx[start_chord]

    # we calculate the transpose value for the chords

    is_complex = False

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
            is_complex = True

        song_chord_list.append(new_root + mode + rest)

    if is_complex:
        complex_nr += 1
        complex_chord_dict[elem] = song_chord_list
    else:
        simple_nr += 1
        simple_chord_dict[elem] = song_chord_list

show = input("Do you want to see statistics? Y/n")

if show == 'Y':
    print("complex_nr", complex_nr)
    print("simple_nr", simple_nr)

    print("absolute songs", absolute_songs)
    print("total songs", total_songs)
    print("tonality specified", tonality_specified)
    print("no tonality specified", no_tonality_specified)
    print("no tonality songs", no_tonality_songs)
    print("minor songs", minor_songs)
    print("major songs", major_songs)

save = input("do you want to save the data? Y/n")

if save == 'Y':
    try:
        with open(os.path.join(c.project_folder, "web_scraping/simple_chords_C.json"), 'w') as fp:
            fp.write(json.dumps(simple_chord_dict))
    except:
        traceback.print_exc()

    try:
        with open(os.path.join(c.project_folder, "web_scraping/complex_chords_C.json"), 'w') as fp:
            fp.write(json.dumps(complex_chord_dict))
    except:
        traceback.print_exc()
