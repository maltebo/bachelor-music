import os
import threading


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def show_in_musescore(m21_object):
    t = threading.Thread(target=_show_in_musescore, args=(m21_object,))
    t.start()


def _show_in_musescore(m21_object):
    m21_object.show()


def round_to_quarter(value):
    return round(value * 4) / 4


class FileNotFittingSettingsError(BaseException):

    def __init__(self, *args):
        super().__init__(*args)
