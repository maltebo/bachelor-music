import os


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def round_to_quarter(value):
    return round(value * 4) / 4


class FileNotFittingSettingsError(BaseException):

    def __init__(self, *args):
        super().__init__(*args)
