import os
import settings.constants_model as c
import json
import music_utils.simple_classes as simple
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.patches import Patch
import statistics as stat

def list_to_note_list(list):
    out = simple.NoteList()
    for elem in list:
        n = simple.Note(elem[0], elem[1], elem[2], elem[3], elem[4])
        out.append(n)
    out.sort()
    return out

pitches = []
pitch_classes = []
lengths = []
offsets = []
rests = []

all_chords = []

for root,_,files in os.walk(os.path.join(c.project_folder, "data/created_songs")):
    for file in files:
        if file.endswith('.json'):
            with open(os.path.join(root, file), 'r') as fp:
                data = json.loads(fp.read())
            melody = data['melody']
            chords = data['chords']

            melody = list_to_note_list(melody)

            for note in melody:
                if note.pitch != 200:
                    pitches.append(note.pitch)
                    pitch_classes.append(note.pitch % 12)
                    rests.append(1)
                else:
                    rests.append(0)
                lengths.append(note.length * 4)
                offsets.append((note.offset % 4) * 4)
            all_chords.extend(chords)


###################################################
############## PITCHES
###################################################
co = Counter(pitches)
plt.bar(co.keys(), co.values())
plt.title("Pitches in MIDI notation: self-extracted melodies")
plt.ylabel("number of occurences")
plt.axvline(stat.mean(pitches), color='green', linewidth=2)
plt.annotate('Mean: {:0.2f}'.format(stat.mean(pitches)), xy=(stat.mean(pitches), 0.7), xytext=(30, 15),
            xycoords=('data', 'axes fraction'), textcoords='offset points',
            horizontalalignment='left', verticalalignment='center',
            arrowprops=dict(arrowstyle='->', fc='black', shrinkA=0, shrinkB=0,)
            )
plt.tight_layout()
plt.show()

###################################################
############## PITCH CLASSES
###################################################
plt.title('Pitch classes')
co = Counter(pitch_classes)
plt.bar(list(co.keys()), list(co.values()))
plt.show()

###################################################
############## NOTE LENGTHS
###################################################
co = Counter(lengths)
plt.bar(co.keys(), co.values())
plt.title("Lengths: melodies created by the model")
plt.ylabel("number of occurences")
plt.xlabel("sixteenth notes")
plt.tight_layout()
plt.show()

###################################################
############## OFFSETS
###################################################

plt.title('Offsets')
co = Counter(offsets)
co = sorted(co.items())
d = '#1fb45d'
b = '#1f77b4'
h = '#871fb4'
s = '#3d1fb4'
color = [d,s,h,s,b,s,h,s,d,s,h,s,b,s,h,s]
x, y = zip(*list(co))
plt.bar(x, y, color=color)
plt.title("Offsets: melodies created by the model")
plt.ylabel("number of occurences")
plt.xlabel("sixteenth notes from beginning of measure")
legend_elements = [Patch(facecolor=d, edgecolor=d,
                         label='Downbeats'),
                    Patch(facecolor=b, edgecolor=b,
                          label='Beat 1 and 3'),
                    Patch(facecolor=h, edgecolor=h,
                          label='Half beats'),
                    Patch(facecolor=s, edgecolor=s,
                          label='Sixteenth beats')
                    ]
plt.legend(handles=legend_elements, loc=1)
plt.tight_layout()
plt.show()

###################################################
############## CHORDS
###################################################
plt.title('Chords')
co = Counter(all_chords)
plt.bar(list(co.keys()), list(co.values()))
plt.show()