import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import settings.constants as c

with open(os.path.join(c.project_folder, "preprocessing/melody_and_chords/melody_stat_data.json"), 'r') as fp:
    stat_data = json.load(fp)

full_data = []

for filename in stat_data:

    # average length
    all_lengths = stat_data[filename]["avg_length_mel"] + stat_data[filename]["avg_length_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["avg_length_mel_norm"] = [0.5] * len(stat_data[filename]["avg_length_mel"])
        stat_data[filename]["avg_length_har_norm"] = [0.5] * len(stat_data[filename]["avg_length_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["avg_length_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["avg_length_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["avg_length_mel_norm"] = temp_mel
        stat_data[filename]["avg_length_har_norm"] = temp_har

    # average different length
    all_lengths = stat_data[filename]["avg_diff_length_mel"] + stat_data[filename]["avg_diff_length_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["avg_diff_length_mel_norm"] = [0.5] * len(stat_data[filename]["avg_diff_length_mel"])
        stat_data[filename]["avg_diff_length_har_norm"] = [0.5] * len(stat_data[filename]["avg_diff_length_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["avg_diff_length_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["avg_diff_length_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["avg_diff_length_mel_norm"] = temp_mel
        stat_data[filename]["avg_diff_length_har_norm"] = temp_har

    # average different pitch
    all_lengths = stat_data[filename]["avg_diff_pitch_mel"] + stat_data[filename]["avg_diff_pitch_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["avg_diff_pitch_mel_norm"] = [0.5] * len(stat_data[filename]["avg_diff_pitch_mel"])
        stat_data[filename]["avg_diff_pitch_har_norm"] = [0.5] * len(stat_data[filename]["avg_diff_pitch_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["avg_diff_pitch_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["avg_diff_pitch_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["avg_diff_pitch_mel_norm"] = temp_mel
        stat_data[filename]["avg_diff_pitch_har_norm"] = temp_har

    # average volume
    all_lengths = stat_data[filename]["avg_volume_mel"] + stat_data[filename]["avg_volume_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["avg_volume_mel_norm"] = [0.5] * len(stat_data[filename]["avg_volume_mel"])
        stat_data[filename]["avg_volume_har_norm"] = [0.5] * len(stat_data[filename]["avg_volume_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["avg_volume_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["avg_volume_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["avg_volume_mel_norm"] = temp_mel
        stat_data[filename]["avg_volume_har_norm"] = temp_har
    #
    # average pitch
    all_lengths = stat_data[filename]["avg_pitch_mel"] + stat_data[filename]["avg_pitch_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["avg_pitch_mel_norm"] = [0.5] * len(stat_data[filename]["avg_pitch_mel"])
        stat_data[filename]["avg_pitch_har_norm"] = [0.5] * len(stat_data[filename]["avg_pitch_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["avg_pitch_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["avg_pitch_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["avg_pitch_mel_norm"] = temp_mel
        stat_data[filename]["avg_pitch_har_norm"] = temp_har

    # nr_rests
    all_lengths = stat_data[filename]["nr_rests_mel"] + stat_data[filename]["nr_rests_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["nr_rests_mel_norm"] = [0.5] * len(stat_data[filename]["nr_rests_mel"])
        stat_data[filename]["nr_rests_har_norm"] = [0.5] * len(stat_data[filename]["nr_rests_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["nr_rests_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["nr_rests_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["nr_rests_mel_norm"] = temp_mel
        stat_data[filename]["nr_rests_har_norm"] = temp_har

    # overlapping notes
    all_lengths = stat_data[filename]["overlapping_notes_mel"] + stat_data[filename]["overlapping_notes_har"]
    min_l = min(all_lengths)
    max_l = max(all_lengths)
    if min_l == max_l:
        stat_data[filename]["overlapping_notes_mel_norm"] = [0.5] * len(stat_data[filename]["overlapping_notes_mel"])
        stat_data[filename]["overlapping_notes_har_norm"] = [0.5] * len(stat_data[filename]["overlapping_notes_har"])
    else:
        temp_mel = []
        temp_har = []
        for elem in stat_data[filename]["overlapping_notes_mel"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_mel.append(elem)
        for elem in stat_data[filename]["overlapping_notes_har"]:
            elem = (elem - min_l) / (max_l - min_l)
            temp_har.append(elem)
        stat_data[filename]["overlapping_notes_mel_norm"] = temp_mel
        stat_data[filename]["overlapping_notes_har_norm"] = temp_har

    for elem in zip(stat_data[filename]["avg_length_mel"],
                    stat_data[filename]["avg_diff_length_mel"],
                    stat_data[filename]["avg_diff_pitch_mel"],
                    stat_data[filename]["avg_volume_mel"],
                    stat_data[filename]["avg_pitch_mel"],
                    stat_data[filename]["nr_rests_mel"],
                    stat_data[filename]["overlapping_notes_mel"],
                    stat_data[filename]["avg_length_mel_norm"],
                    stat_data[filename]["avg_diff_length_mel_norm"],
                    stat_data[filename]["avg_diff_pitch_mel_norm"],
                    stat_data[filename]["avg_volume_mel_norm"],
                    stat_data[filename]["avg_pitch_mel_norm"],
                    stat_data[filename]["nr_rests_mel_norm"],
                    stat_data[filename]["overlapping_notes_mel_norm"]
                    ):
        full_data.append((elem, 'Melody'))

    for elem in zip(stat_data[filename]["avg_length_har"],
                    stat_data[filename]["avg_diff_length_har"],
                    stat_data[filename]["avg_diff_pitch_har"],
                    stat_data[filename]["avg_volume_har"],
                    stat_data[filename]["avg_pitch_har"],
                    stat_data[filename]["nr_rests_har"],
                    stat_data[filename]["overlapping_notes_har"],
                    stat_data[filename]["avg_length_har_norm"],
                    stat_data[filename]["avg_diff_length_har_norm"],
                    stat_data[filename]["avg_diff_pitch_har_norm"],
                    stat_data[filename]["avg_volume_har_norm"],
                    stat_data[filename]["avg_pitch_har_norm"],
                    stat_data[filename]["nr_rests_har_norm"],
                    stat_data[filename]["overlapping_notes_har_norm"]
                    ):
        full_data.append((elem, 'No Melody'))

labels = ['avg_length', 'avg_diff_length', 'avg_diff_pitch', 'avg_volume', 'avg_pitch', 'nr_rests', 'overlapping',
          'avg_length_norm', 'avg_diff_length_norm', 'avg_diff_pitch_norm', 'avg_volume_norm', 'avg_pitch_norm',
          'nr_rests_norm', 'overlapping_norm', 'class']

df = pd.DataFrame.from_records([list(elem[0]) + [elem[1]] for elem in full_data], columns=labels)

from sklearn.utils import shuffle

df = shuffle(df)

draw = input("Do you want to plot the data? Y/n")

if draw == 'Y':
    plot = sns.pairplot(df, hue='class', diag_kind='kde')
    plt.savefig(os.path.join(c.project_folder, "preprocessing/melody_and_chords/melody_parameters_pairplot_norm.png"),
                dpi=350, bbox_inches='tight')
    plt.show()

    sns.heatmap(df.corr(), annot=None)
    plt.savefig(os.path.join(c.project_folder, "preprocessing/melody_and_chords/melody_parameters_heatmap_norm.png"),
                dpi=350, bbox_inches='tight')
    plt.show()

train = input("Do you want to start training the neural network? Y/n")
if train != 'Y':
    import sys

    sys.exit(0)

X = df.iloc[:, 0:14]
y = df.iloc[:, 14]

class_weight = {0: 1.0,
                1: 2.0}

# print(y)

# standardizing the input feature
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
X = sc.fit_transform(X)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

from keras import Sequential
from keras.layers import Dense, Dropout

classifier = Sequential()
# First Hidden Layer
classifier.add(Dense(64, activation='relu', kernel_initializer='truncated_normal', input_dim=14))

classifier.add(Dropout(rate=0.2))

classifier.add(Dense(64, activation='relu', kernel_initializer='truncated_normal'))

classifier.add(Dropout(rate=0.2))

# Output Layer
classifier.add(Dense(1, activation='sigmoid', kernel_initializer='truncated_normal'))

# Compiling the neural network
classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Fitting the data to the training dataset
classifier.fit(X_train, y_train, batch_size=10, epochs=100, class_weight=class_weight)

eval_model = classifier.evaluate(X_train, y_train)
print("Eval model:", eval_model)

eval_model = classifier.evaluate(X_test, y_test)
print("Eval model test data:", eval_model)

y_pred = classifier.predict(X_test)

y_pred = (y_pred > 0.5)

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)
print('Confusion Matrix:\n', cm)

##############################################################################

# find and delete duplicates from the data -> put into deleted pieces folder
#
# print(len(stat_data))
#
# data_list = []
# file_name_list = []
#
# for data in stat_data:
#     if stat_data[data] not in data_list:
#         data_list.append(stat_data[data])
#         file_name_list.append(data)
#
# print(len(file_name_list))
#
# duplicates = [elem for elem in stat_data if elem not in file_name_list]
#
# for d in duplicates:
#
#     del stat_data[d]
#
# with open(os.path.join(c_m.project_folder, "preprocessing/melody_and_chords/melody_stat_data.json"), 'w') as fp:
#     fp.write(json.dumps(stat_data, indent=2))
