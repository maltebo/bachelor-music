# bachelor-music

The aim of this project is to create computer-generated music based on a user database of midi or 
[.mxl-files](https://www.musicxml.com/). If you are using .mxl-files, the download of the current 
[MuseScore](https://musescore.org/en) version is required. Other needed imports are 
[tensorflow](https://www.tensorflow.org/install) and 
[music21](https://web.mit.edu/music21/doc/usersGuide/usersGuide_01_installing.html#usersguide-01-installing "Installing music21").

Currently, to start the whole process you need to call preprocessing.make_data_from_mxl_archive and 
set the path to your mxl data directory. However, this will be changed in further versions.

To create .mxl-data from your midi files, you need to do a bit more work, changing a few parameters 
in midi_to_mxl.sh and midi_to_mxl.py. This is only recommended for people with a programming background, 
as it might be quite complicated to date.
