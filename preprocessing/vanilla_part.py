from music21 import *
from preprocessing.helper import round_to_quarter


class VanillaPart(stream.Part):

    def __init__(self):
        stream.Part.__init__(self)
        self.pitch_list = []
        self.volume_list = []
        self.note_number = 0
        self.total_notes_or_chords = 0
        self.total_pitches = 0
        self.lyrics_number = 0
        self.note_lengths = []
        self.key = None
        self.key_correlation = None

    def insert_local(self, elem):
        if type(elem) == note.Note:
            self.insert_note(elem)
        elif type(elem) == chord.Chord:
            self.insert_chord(elem)
        else:
            raise ValueError("That was not the thing we expected you to do...")

    def insert_note(self, elem: note.Note):
        start = elem.offset
        end = start + elem.quarterLength
        temp_volume = elem.volume.cachedRealized
        temp_lyrics = elem.lyrics
        temp_pitch = elem.pitch.ps

        temp_note = self.create_note(start, end, temp_volume, temp_lyrics, temp_pitch)

        if not temp_note:
            return

        self.pitch_list.append(temp_pitch)
        self.volume_list.append(temp_volume)
        self.note_number += 1
        self.total_notes_or_chords += 1
        self.total_pitches += 1
        try:
            self.note_lengths.append(elem.seconds)
        except exceptions21.Music21Exception:
            pass

        if temp_lyrics:
            self.lyrics_number += 1

        super().insert(temp_note)

    def insert_chord(self, elem: chord.Chord):
        start = elem.offset
        end = start + elem.quarterLength
        temp_volume = elem.volume.cachedRealized
        temp_lyrics = elem.lyrics

        for temp_full_pitch in elem.pitches:

            temp_pitch = temp_full_pitch.ps

            temp_note = self.create_note(start, end, temp_volume, temp_lyrics, temp_pitch)

            if not temp_note:
                return

            self.pitch_list.append(temp_pitch)
            self.total_pitches += 1
            super().insert(temp_note)

        self.volume_list.append(temp_volume)
        self.total_notes_or_chords += 1

        if temp_lyrics:
            self.lyrics_number += 1

    @staticmethod
    def create_note(start, end, temp_volume, temp_lyrics, temp_pitch):
        if end - start < 0.2:
            return None

        temp_note = note.Note()

        temp_note.offset = round_to_quarter(start)
        new_end = round_to_quarter(end)
        new_duration = new_end - temp_note.offset
        if new_duration < 0.25:
            return None

        temp_note.quarterLength = new_duration

        temp_note.volume = temp_volume
        if temp_lyrics:
            temp_note.lyrics = temp_lyrics

        temp_note.pitch.ps = temp_pitch

        return temp_note

