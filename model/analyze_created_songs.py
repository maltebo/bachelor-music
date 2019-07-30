import os
import settings.constants_model as c
import json
import music_utils.simple_classes as simple
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.patches import Patch
import statistics as stat
import model.converting as converter

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
c_n = Counter(pitch_classes)
c_n2 = c_n.most_common()
labels = [c.idx_to_chord[cc] for cc, _ in c_n2[:9]] + ['Rest']


prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

temp = {ch: co for ch, co in zip(labels, colors)}
# labels = [l.replace('b', '$\musFlat{}$') for l in labels]

sizes = [cc for _,cc in c_n2[:9]] + [sum([cc for _,cc in c_n2[9:]])]

patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc="best")
plt.axis('equal')
plt.title("Distribution of notes: self-extracted melodies")
plt.tight_layout()
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/notes_no_lyrics.pdf')
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/notes_no_lyrics.pgf')
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
############## REST/NOTE RATIO
###################################################

c_r = Counter(rests)
x = ["Rest", "Note"]
if list(c_r.keys())[0] == 0:
    x = ["Note", "Rest"]
plt.title("Rest and note distribution")
plt.bar([1.0, 2.0], [cc/sum(c_r.values()) for cc in c_r.values()],width=0.35, label="self-extracted melodies")
plt.xticks([1,2], x)
plt.ylabel("percentage")
plt.legend()
plt.tight_layout()
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/rest_note_all.pdf')
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/rest_note_all.pgf')
plt.show()

###################################################
############## CHORDS
###################################################

chords_trans = [ch for i, ch in enumerate(all_chords[:-1]) if all_chords[i+1] != ch]

c_c = Counter(all_chords)
c_c2 = c_c.most_common()
#
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

labels = [converter.id_to_chord[ch] for ch, _ in c_c2[:9]] + ['Rest']
#
temp = {ch: co for ch, co in zip(labels, colors)}
#
sizes = [ccc for _, ccc in c_c2[:9]] + [sum([ccc for _,ccc in c_c2[9:]])]
patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc="best", ncol=2)
plt.axis('equal')
plt.tight_layout()
plt.title("Chords created with algorithm")
plt.tight_layout()
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chords_all.pdf')
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chords_all.pgf')
plt.show()

c_c = Counter(chords_trans)
c_c2 = c_c.most_common()

all_chords = {converter.id_to_chord[n]: x/len(chords_trans) for n, x in c_c2}

labels = [converter.id_to_chord[ch] for ch, _ in c_c2[:9]] + ['Rest']
colors = []
for l in labels:
    if l in temp:
        colors.append(temp[l])
    else:
        colors.append((1,0,0))

sizes = [ccc for _, ccc in c_c2[:9]] + [sum([ccc for _,ccc in c_c2[9:]])]
patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc=1, ncol=2)
plt.axis('equal')
plt.tight_layout()
plt.title("Chord transitions created with algorithm")
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chords_trans.pdf')
# plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FirstDraft/figures/chords_trans.pgf')
plt.show()