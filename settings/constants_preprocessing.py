import settings.music_info_pb2 as music_info
from settings.constants import *
from settings.music_info_pb2 import Settings

# needed for creation and preprocessing of data
UPDATE = True
UPDATE_FREQUENCY = 1

# for trying out new settings

DRAFT = False


def make_settings() -> Settings:
    '''
    makes current settings and saves them in protobuffer
    :return: protobuffer with current settings
    '''
    settings = Settings()
    settings.min_pitch = 49.0
    settings.max_pitch = 84.0
    settings.delete_part_threshold = 0.65
    settings.delete_stream_threshold = 0.8
    settings.accepted_key = "C major"
    settings.min_bpm = 100
    settings.max_bpm = 140
    settings.valid_time = "4_4"
    return settings


music_settings = make_settings()

if DRAFT:
    settings_filename = 'DRAFT_'
else:
    settings_filename = ''
settings_filename += str(round(music_settings.delete_part_threshold, 2))
settings_filename += '_' + str(round(music_settings.delete_stream_threshold, 2))
settings_filename += '_' + music_settings.accepted_key
settings_filename += '_' + str(music_settings.min_bpm)
settings_filename += '_' + str(music_settings.max_bpm)
settings_filename += '_' + music_settings.valid_time
settings_filename += '.pb'

music_info_dict_lock = threading.Lock()
music_info_file_lock = threading.Lock()
melody_lock = threading.Lock()

music_protocol_buffer = None

# find the current music list if it exists

for dirpath, _, filenames in os.walk(MUSIC_INFO_FOLDER_PATH):

    for filename in filenames:

        if filename == settings_filename:
            if os.path.getsize(os.path.join(dirpath, filename)) == 0:
                os.remove(os.path.join(dirpath, filename))
                break
            with open(os.path.join(dirpath, filename), 'rb') as fp:
                music_protocol_buffer = music_info.MusicList()
                music_protocol_buffer.ParseFromString(fp.read())
                music_protocol_buffer.counter = 0
            break

existing_files = {}


def make_music_list():
    ml = music_info.MusicList(settings=music_settings, counter=0)
    return ml


# location of the music protocol buffer.
# TODO: Where do we need this?
PROTOCOL_BUFFER_LOCATION = os.path.join(MUSIC_INFO_FOLDER_PATH, settings_filename)

# if there has not been a protobuffer yet, create one and save it (?)
# TODO: do we always need this?
if not music_protocol_buffer:

    create_mi = input("Do you want to create a music info file? Y/n")

    if create_mi == 'Y':
        music_protocol_buffer = make_music_list()

        with open(PROTOCOL_BUFFER_LOCATION, 'xb') as fp:
            fp.write(music_protocol_buffer.SerializeToString())

else:
    # create a list of all existing files
    for f in music_protocol_buffer.music_data:
        existing_files[f.filepath] = f.valid

mxl_work_queue = queue.Queue(0)
mxl_files_done = 0
mxl_dict = {}

proto_buffer_work_queue = queue.Queue(0)
proto_buffers_done = 0

melody_work_queue = queue.Queue(0)
melodies_done = 0

for root, dirs, files in os.walk(MXL_DATA_FOLDER):
    for file in files:
        if file.split('.')[0].split(b'_tf_skyline')[0] in mxl_dict:
            mxl_dict[file.split('.')[0].split(b'_tf_skyline')[0]].append(os.path.join(root, file))
        else:
            mxl_dict[file.split('.')[0].split(b'_tf_skyline')[0]] = [os.path.join(root, file)]
        # if file.endswith('.mxl'):
        #     mxl_work_queue.put(os.path.join(root, file))
        # if file.endswith('.pb'):
        #     proto_buffer_work_queue.put(os.path.join(root, file))
        # elif file.endswith(('.melody_pb')):
        #     melody_work_queue.put(os.path.join(root, file))
        # take for every song only one version into account!
        # break

mxl_start_time = time.time()

proto_buffers_to_do = proto_buffer_work_queue.qsize()
proto_buffer_start_time = mxl_start_time

melodies_to_do = melody_work_queue.qsize()
melodies_start_time = mxl_start_time

del_list = []

for file in mxl_dict:
    mxl_files = []
    protofiles = []
    melody_files = []
    done = False
    valid = False

    for f in mxl_dict[file]:
        if f.endswith('.mxl'):
            if os.path.relpath(f, MXL_DATA_FOLDER) in existing_files:
                done = True
                valid = existing_files[os.path.relpath(f, MXL_DATA_FOLDER)]
            mxl_files.append(f.split('.')[0])
        elif f.endswith('.pb'):
            protofiles.append(f.split('.')[0])
        elif f.endswith('.melody_pb'):
            melody_files.append(f.split('.')[0].split('_tf_skyline')[0])

    check_ex = input("Do you want to check existence and delete data from protobuffer? Y/n")
    if check_ex == 'Y':

        if done:
            if not valid:
                del_list.extend(mxl_dict[file])
            else:
                ref = ""
                if melody_files:
                    ref = melody_files[0]
                elif protofiles:
                    ref = protofiles[0]
                else:
                    print("No protobuffer for valid and done file", file)
                    for f in music_protocol_buffer.music_data:
                        if f.filepath == mxl_dict[file][0].split('lmd_matched_mxl/')[-1]:
                            f.filepath = "Deleted"
                            f.valid = False
                            f.ClearField('min_metronome')
                            f.ClearField('max_metronome')
                            f.ClearField('key_correlation')
                            f.ClearField('parts')
                            with open(PROTOCOL_BUFFER_LOCATION, 'wb') as fp:
                                fp.write(music_protocol_buffer.SerializeToString())
                            break
                    # raise ValueError("There should be at least one protobuffer in this case")

                for f in mxl_dict[file]:
                    if not f.startswith(ref):
                        del_list.append(f)
        else:
            del_list.extend(mxl_dict[file][1:])
            try:
                print(mxl_files[0] + b'.mxl')
                mxl_work_queue.put(mxl_files[0] + b'.mxl')
            except IndexError:
                print(mxl_dict[file])
                print("No mxl file for file:", file)

mxl_files_to_do = mxl_work_queue.qsize()

if len(del_list) > 0:
    print(str(len(del_list)), "files will be moved to the deleted files folder. Alright?")
    print("First 10 Elements:", del_list[:10])
    i = input("Y for yes")
    if i == 'Y':
        for f in del_list:
            split_file = f.split('/')
            folder = '/'.join(split_file[-5:-1])
            filename = split_file[-1]
            os.makedirs(os.path.join(DELETED_PIECES_PATH, folder), exist_ok=True)
            os.rename(f, os.path.join(os.path.join(DELETED_PIECES_PATH, folder), filename))
    else:
        print("No files moved")
