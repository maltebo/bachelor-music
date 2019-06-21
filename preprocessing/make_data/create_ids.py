import os

import settings.constants as c


def create_IDs():
    ID_dict = {}

    my_queue = c.mxl_work_queue

    while not my_queue.empty():
        file_name = my_queue.get()
        ID = os.path.split(file_name)[1].split('.')[0]

        if ID in ID_dict:
            print('WTF')
            print(file_name)
            print(ID_dict[ID])
        ID_dict[ID] = file_name

    return ID_dict


if __name__ == '__main__':

    print("Start creating IDs")

    ID_dict = create_IDs()

    print(len(ID_dict))

    # from tempfile import TemporaryFile
    #
    # with TemporaryFile() as outfile:
    #
    #     np.save(outfile, [1,2,3,4,0x5454])
    #
    #     outfile.seek(0)
    #
    #     print(np.load(outfile))

    l = []

    for root, dirs, files in os.walk(c.MXL_DATA_FOLDER):
        for file in files:
            if file.endswith('.mxl'):
                l.append(os.path.join(root, file))

    print(len(l))
