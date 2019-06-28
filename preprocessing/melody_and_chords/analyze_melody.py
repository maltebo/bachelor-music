import json
import os
from statistics import mean

import matplotlib.pyplot as plt

import music_utils.simple_classes as simple
import preprocessing.melody_and_chords.find_melody as find_melody
import settings.constants as c
from settings.music_info_pb2 import VanillaStreamPB


def average_note_length(melody: simple.NoteList):
    return mean([n.length for n in melody if n.pitch < 129])


def average_different(pitch_list):
    res = []
    for elem in pitch_list:
        res.append(len(set(elem)))
    return mean(res)


if __name__ == '__main__':

    my_queue = c.proto_buffer_work_queue
    stat_data = {}

    i = 0
    # while i < 10:
    while not my_queue.empty():

        filename = my_queue.get()

        assert filename.endswith(".pb")

        proto_buffer_path = filename

        with open(proto_buffer_path, 'rb') as fp:
            proto_buffer = VanillaStreamPB()
            proto_buffer.ParseFromString(fp.read())
            assert proto_buffer.HasField('info')

        simple_song = simple.Song(proto_buffer)

        lyrics, full_melody = find_melody.skyline_advanced(simple_song, split=False)

        if not lyrics:
            # print("\nNo lyrics found!\n")
            continue
        else:
            print(filename)
            # print("\nLyrics found!\n")

        melody_parts = set()

        for elem in full_melody:
            if elem[1]:
                melody_parts.add(elem[1][0].part)

        if not melody_parts:
            continue

        i += 1

        # calculate average note length over melody line & over all other lines
        stat_data[filename] = {"avg_length_mel": [],
                               "avg_length_har": [],
                               "avg_diff_length_mel": [],
                               "avg_diff_length_har": [],
                               "avg_diff_pitch_mel": [],
                               "avg_diff_pitch_har": [],
                               "avg_volume_mel": [],
                               "avg_volume_har": [],
                               "avg_pitch_mel": [],
                               "avg_pitch_har": [],
                               "nr_rests_mel": [],
                               "nr_rests_har": [],
                               "overlapping_notes_mel": [],
                               "overlapping_notes_har": [],
                               }
        for part in simple_song.parts:

            part_notes = part.notes(exclude_rests=True)

            values = set(map(lambda x: int(x[0] / 4.0), part_notes))

            # print("Values:", values)

            length_list = [[y[1] for y in part_notes if int(y[0] / 4.0) == x] for x in values]
            pitch_list = [[y[2] % 12 for y in part_notes if int(y[0] / 4.0) == x] for x in values]
            volume_list = [y[3] for y in part_notes]

            # print(length_list)
            # print(pitch_list)
            # print(volume_list)

            avg_length = average_note_length(part_notes)
            avg_diff_pitch = average_different(pitch_list)
            avg_diff_length = average_different(length_list)
            avg_volume = mean(volume_list)
            avg_pitch = mean([y[2] for y in part_notes])

            number_of_rests = len([1 for (n1, n2) in zip(part_notes[:-1], part_notes[1:])
                                   if n1.offset + n1.length < n2.offset]) / len(part_notes)

            percentage_overlapping_notes = 0
            last_sounding = 0
            for n1 in part_notes:
                if n1.offset < last_sounding:
                    percentage_overlapping_notes += 1
                if n1.end() > last_sounding:
                    last_sounding = n1.end()

            percentage_overlapping_notes /= len(part_notes)

            if part.id in melody_parts:
                stat_data[filename]["avg_length_mel"].append(avg_length)
                stat_data[filename]["avg_diff_length_mel"].append(avg_diff_length)
                stat_data[filename]["avg_diff_pitch_mel"].append(avg_diff_pitch)
                stat_data[filename]["avg_volume_mel"].append(avg_volume)
                stat_data[filename]["avg_pitch_mel"].append(avg_pitch)
                stat_data[filename]["nr_rests_mel"].append(number_of_rests)
                stat_data[filename]["overlapping_notes_mel"].append(percentage_overlapping_notes)

            else:
                stat_data[filename]["avg_length_har"].append(avg_length)
                stat_data[filename]["avg_diff_length_har"].append(avg_diff_length)
                stat_data[filename]["avg_diff_pitch_har"].append(avg_diff_pitch)
                stat_data[filename]["avg_volume_har"].append(avg_volume)
                stat_data[filename]["avg_pitch_har"].append(avg_pitch)
                stat_data[filename]["nr_rests_har"].append(number_of_rests)
                stat_data[filename]["overlapping_notes_har"].append(percentage_overlapping_notes)

    avg_lengths_mel = []
    avg_lengths_har = []

    avg_diff_pitch_mel = []
    avg_diff_pitch_har = []

    avg_diff_length_mel = []
    avg_diff_length_har = []

    avg_volume_mel = []
    avg_volume_har = []

    avg_pitch_mel = []
    avg_pitch_har = []

    nr_rests_mel = []
    nr_rests_har = []

    overlapping_notes_mel = []
    overlapping_notes_har = []

    for elem in stat_data:
        avg_lengths_mel.extend(stat_data[elem]["avg_length_mel"])
        avg_lengths_har.extend(stat_data[elem]["avg_length_har"])

        avg_diff_length_mel.extend(stat_data[elem]["avg_diff_length_mel"])
        avg_diff_length_har.extend(stat_data[elem]["avg_diff_length_har"])

        avg_diff_pitch_mel.extend(stat_data[elem]["avg_diff_pitch_mel"])
        avg_diff_pitch_har.extend(stat_data[elem]["avg_diff_pitch_har"])

        avg_volume_mel.extend(stat_data[elem]["avg_volume_mel"])
        avg_volume_har.extend(stat_data[elem]["avg_volume_har"])

        avg_pitch_mel.extend(stat_data[elem]["avg_pitch_mel"])
        avg_pitch_har.extend(stat_data[elem]["avg_pitch_har"])

        nr_rests_mel.extend(stat_data[elem]["nr_rests_mel"])
        nr_rests_har.extend(stat_data[elem]["nr_rests_har"])

        overlapping_notes_mel.extend(stat_data[elem]["overlapping_notes_mel"])
        overlapping_notes_har.extend(stat_data[elem]["overlapping_notes_har"])

    fig, ((ax0, ax1), (ax2, ax3), (ax4, ax5), (ax6, ax7)) = plt.subplots(nrows=4, ncols=2, sharex=False, sharey=True)

    ax0.set_title("Average lengths of notes")
    ax0.plot(avg_lengths_mel, [1] * len(avg_lengths_mel), 'bs', avg_lengths_har, [0] * len(avg_lengths_har), 'g^')
    ax0.boxplot([avg_lengths_mel, avg_lengths_har], positions=[1, 0], widths=0.4, vert=False)

    ax1.set_title("Average different lengths per bar")
    ax1.plot(avg_diff_length_mel, [1] * len(avg_diff_length_mel), 'bs', avg_diff_length_har,
             [0] * len(avg_diff_length_har), 'g^')
    ax1.boxplot([avg_diff_length_mel, avg_diff_length_har], positions=[1, 0], widths=0.4, vert=False)

    ax2.set_title("Average different pitches per bar")
    ax2.plot(avg_diff_pitch_mel, [1] * len(avg_diff_pitch_mel), 'bs', avg_diff_pitch_har, [0] * len(avg_diff_pitch_har),
             'g^')
    ax2.boxplot([avg_diff_pitch_mel, avg_diff_pitch_har], positions=[1, 0], widths=0.4, vert=False)

    ax3.set_title("Average volume of parts")
    ax3.plot(avg_volume_mel, [1] * len(avg_volume_mel), 'bs', avg_volume_har, [0] * len(avg_volume_har), 'g^')
    ax3.boxplot([avg_volume_mel, avg_volume_har], positions=[1, 0], widths=0.4, vert=False)

    ax4.set_title("Average pitch")
    ax4.plot(avg_pitch_mel, [1] * len(avg_pitch_mel), 'bs', avg_pitch_har, [0] * len(avg_pitch_har), 'g^')
    ax4.boxplot([avg_pitch_mel, avg_pitch_har], positions=[1, 0], widths=0.4, vert=False)

    ax5.set_title("Percentage of rests")
    ax5.plot(nr_rests_mel, [1] * len(nr_rests_mel), 'bs', nr_rests_har, [0] * len(nr_rests_har), 'g^')
    ax5.boxplot([nr_rests_mel, nr_rests_har], positions=[1, 0], widths=0.4, vert=False)

    ax6.set_title("Percentage of overlapping notes")
    ax6.plot(overlapping_notes_mel, [1] * len(overlapping_notes_mel), 'bs', overlapping_notes_har,
             [0] * len(overlapping_notes_har), 'g^')
    ax6.boxplot([overlapping_notes_mel, overlapping_notes_har], positions=[1, 0], widths=0.4, vert=False)

    plt.savefig(os.path.join(c.project_folder, "preprocessing/melody_and_chords/test_figure.png"),
                dpi=350)
    plt.show()

    with open(os.path.join(c.project_folder, "preprocessing/melody_and_chords/melody_stat_data.json"), 'w') as fp:
        fp.write(json.dumps(stat_data, indent=2))

    print("Number of pieces:", i)
