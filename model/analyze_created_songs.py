import os
import settings.constants_model as c
import json
import music_utils.simple_classes as simple
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.patches import Patch
import statistics as stat
import model.converting as converter
from miscellaneous.analyze import get_full_arrays

def list_to_note_list(list):
    out = simple.NoteList()
    for elem in list:
        n = simple.Note(elem[0], elem[1], elem[2], elem[3], elem[4])
        out.append(n)
    out.sort()
    return out

train_pitches, train_lengths, train_offsets, train_notes, train_rest_or_note, train_chords = get_full_arrays()

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
############## MATPLOTLIB SETUP
###################################################

save = input("Final version? Y/n")

if save == 'Y':
    save = True
    import matplotlib as mpl
    mpl.use("pgf")
    pgf_with_rc_fonts = {
        "font.serif": ['cmr10'],                   # use latex default serif font
        "pgf.preamble": [
                 "\\usepackage{musicography}",
                 ]
    }
    mpl.rcParams.update(pgf_with_rc_fonts)
else:
    save = False

show = False
if not save:
    show = input("Show plots? Y/n")
    if show == 'Y':
        show = True
    else:
        show = False

###################################################
############## PITCHES
###################################################
plt.figure(figsize=(4,4*(3/4)))
co = Counter(pitches)
plt.bar(co.keys(), co.values())
plt.title("Pitches in MIDI notation: created melodies")
plt.ylabel("number of occurences")
plt.axvline(stat.mean(pitches), color='green', linewidth=2)
plt.annotate('Mean: {:0.2f}'.format(stat.mean(pitches)), xy=(stat.mean(pitches), 0.7), xytext=(30, 15),
            xycoords=('data', 'axes fraction'), textcoords='offset points',
            horizontalalignment='left', verticalalignment='center',
            arrowprops=dict(arrowstyle='->', fc='black', shrinkA=0, shrinkB=0,)
            )
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_pitches.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_pitches.pgf')
elif show:
    plt.show()


plt.figure(figsize=(4,4*(3/4)))
co = Counter(train_pitches)
plt.bar(co.keys(), co.values())
plt.title("Pitches in MIDI notation: training melodies")
plt.ylabel("number of occurences")
plt.axvline(stat.mean(train_pitches), color='red', linewidth=2)
plt.annotate('Mean: {:0.2f}'.format(stat.mean(train_pitches)), xy=(stat.mean(train_pitches), 0.7), xytext=(30, 15),
            xycoords=('data', 'axes fraction'), textcoords='offset points',
            horizontalalignment='left', verticalalignment='center',
            arrowprops=dict(arrowstyle='->', fc='black', shrinkA=0, shrinkB=0,)
            )
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_pitches.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_pitches.pgf')
elif show:
    plt.show()

###################################################
############## PITCH CLASSES
###################################################
plt.figure(figsize=(4,4*(3/4)))
c_n = Counter(pitch_classes)
c_n2 = c_n.most_common()
labels = [c.idx_to_chord[cc] for cc, _ in c_n2[:9]] + ['Rest']

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

temp = {ch: co for ch, co in zip(labels, colors)}
if save:
    labels = [l.replace('b', '$\musFlat{}$') for l in labels]

sizes = [cc for _,cc in c_n2[:9]] + [sum([cc for _,cc in c_n2[9:]])]

patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc="best")
plt.axis('equal')
plt.title("Note distribution: created melodies")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_notes.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_notes.pgf')
elif show:
    plt.show()


plt.figure(figsize=(4,4*(3/4)))
c_n = Counter(train_notes)
c_n2 = c_n.most_common()
labels = [c.idx_to_chord[cc] for cc, _ in c_n2[:9]] + ['Rest']

colors = []
for l in labels:
    if l in temp:
        colors.append(temp[l])
    else:
        colors.append((1,0,0))

if save:
    labels = [l.replace('b', '$\musFlat{}$') for l in labels]

sizes = [cc for _,cc in c_n2[:9]] + [sum([cc for _,cc in c_n2[9:]])]

patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc="best")
plt.axis('equal')
plt.title("Note distribution: training melodies")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_notes.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_notes.pgf')
elif show:
    plt.show()

###################################################
############## NOTE LENGTHS
###################################################
plt.figure(figsize=(4,4*(3/4)))
co = Counter(lengths)
plt.bar(co.keys(), co.values())
plt.title("Lengths: created melodies")
plt.ylabel("number of occurences")
plt.xlabel("sixteenth notes")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_length.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_length.pgf')
elif show:
    plt.show()


plt.figure(figsize=(4,4*(3/4)))
co = Counter(train_lengths)
plt.bar(co.keys(), co.values())
plt.title("Lengths: training melodies")
plt.ylabel("number of occurences")
plt.xlabel("sixteenth notes")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_length.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_length.pgf')
elif show:
    plt.show()

###################################################
############## OFFSETS
###################################################
plt.figure(figsize=(4,4*(3/4)))
co = Counter(offsets)
co = sorted(co.items())
d = '#1fb45d'
b = '#1f77b4'
h = '#871fb4'
s = '#3d1fb4'
color = [d,s,h,s,b,s,h,s,d,s,h,s,b,s,h,s]
x, y = zip(*list(co))
plt.bar(x, y, color=color)
plt.title("Offsets: created melodies")
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
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_offsets.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_offsets.pgf')
elif show:
    plt.show()


plt.figure(figsize=(4,4*(3/4)))
co = Counter(train_offsets)
co = sorted(co.items())
d = '#1fb45d'
b = '#1f77b4'
h = '#871fb4'
s = '#3d1fb4'
color = [d,s,h,s,b,s,h,s,d,s,h,s,b,s,h,s]
x, y = zip(*list(co))
plt.bar(x, y, color=color)
plt.title("Offsets: training melodies")
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
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_offsets.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_offsets.pgf')
elif show:
    plt.show()

###################################################
############## REST/NOTE RATIO
###################################################
plt.figure(figsize=(4,4*(3/4)))
c_r = Counter(rests)
l_c_r = Counter(train_rest_or_note)
x = ["Rest", "Note"]
if list(c_r.keys())[0] == 0:
    x = ["Note", "Rest"]
plt.title("Rest and note distribution")
plt.bar([0.8, 1.8], [cc / sum(c_r.values()) for cc in c_r.values()], width=0.35, label="created melodies")
plt.bar([1.2, 2.2], [cc / sum(l_c_r.values()) for cc in l_c_r.values()], width=0.35, label="training melodies")
plt.xticks([1,2], x)
plt.ylabel("percentage")
plt.legend()
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_rest_note.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_rest_note.pgf')
elif show:
    plt.show()

###################################################
############## CHORDS
###################################################
plt.figure(figsize=(4,4*(3/4)))
chords_trans = [ch for i, ch in enumerate(all_chords[:-1]) if all_chords[i+1] != ch]

c_c = Counter(chords_trans)
c_c2 = c_c.most_common()

all_chords = {converter.id_to_chord[n]: x/len(chords_trans) for n, x in c_c2}

print(all_chords)

labels = [converter.id_to_chord[ch] for ch, _ in c_c2[:9]] + ['Rest']

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

temp = {ch: co for ch, co in zip(labels, colors)}

if save:
    labels = [l.replace('b', '$\musFlat{}$') for l in labels]

sizes = [ccc for _, ccc in c_c2[:9]] + [sum([ccc for _,ccc in c_c2[9:]])]
patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc=1, ncol=2)
plt.axis('equal')
# plt.title("Chord transitions created with algorithm")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_chords_trans.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/created_chords_trans.pgf')
elif show:
    plt.show()



plt.figure(figsize=(4,4*(3/4)))
chords_trans = [ch for i, ch in enumerate(train_chords[:-1]) if train_chords[i+1] != ch]

c_c = Counter(chords_trans)
c_c2 = c_c.most_common()

colors = []

train_chords = {converter.id_to_chord[n]: x/len(chords_trans) for n, x in c_c2}

labels = [converter.id_to_chord[ch] for ch, _ in c_c2[:9]] + ['Rest']

for l in labels:
    if l in temp:
        colors.append(temp[l])
    else:
        colors.append((1,0,0))

if save:
    labels = [l.replace('b', '$\musFlat{}$') for l in labels]

sizes = [ccc for _, ccc in c_c2[:9]] + [sum([ccc for _,ccc in c_c2[9:]])]
patches, texts = plt.pie(sizes, shadow=True, startangle=90, counterclock=False, colors=colors)
plt.legend(patches, labels, loc=1, ncol=2)
plt.axis('equal')
# plt.title("Chord transitions created with algorithm")
plt.tight_layout()
if save:
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_chords_trans.pdf')
    plt.savefig('/home/malte/Documents/Bachelor/BachelorThesis/FinalVersion/figures/trained_chords_trans.pgf')
elif show:
    plt.show()