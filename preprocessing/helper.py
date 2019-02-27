import os
import threading
import preprocessing.constants as c


def remove(file_path, reason):
    new_dir = os.path.join(c.Test.DELETED_TEST_DATA_FOLDER.value, reason)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir, exist_ok=True)
    new_file_path = os.path.join(new_dir, os.path.basename(file_path))
    os.rename(file_path, new_file_path)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def show_in_musescore(m21_object):
    t = threading.Thread(target=_show_in_musescore, args=(m21_object,))
    t.start()


def _show_in_musescore(m21_object):
    m21_object.show()


def round_to_quarter(value):
    return round(value * 4) / 4
