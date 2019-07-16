
from settings.constants import *
import settings.music_info_pb2 as music_info

##################################################################
################ MODEL CONSTANTS
##################################################################

sequence_length = 50
chord_sequence_length = 30

all_files = []
for folder, _, files in os.walk(os.path.join(project_folder, "data/preprocessed_data")):
    for file in files:
        if file.endswith('.pb'):
            all_files.append(os.path.join(folder, file))

if not all_files:
    raise FileNotFoundError("No full datafile available; should be in data/preprocessed_data")

all_files = sorted(all_files, reverse=True)

current_pb = all_files[0]

all_data = music_info.AllData()
with open(current_pb, 'rb') as fp:
    all_data.ParseFromString(fp.read())

del all_files
del current_pb