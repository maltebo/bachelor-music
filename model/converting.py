pitch_to_id = {i+1 : i+48 for i in range(37)}
pitch_to_id[0] = 200
id_to_pitch = {y: x for x, y in pitch_to_id.items()}

length_to_id = {i+1: i for i in range(16)}
id_to_length = {y: x for x, y in length_to_id.items()}

chord_to_id = {'C': 0, 'F': 1, 'G': 2, 'Am': 3, 'E': 4, 'Dm': 5, 'Bb': 6, 'Gm': 7, 'Eb': 8, 'D': 9,
               'Em': 10, 'Bm': 11, 'A': 12, 'Ab': 13, 'Abm': 14, 'Cm': 15, 'B': 16, 'Dbm': 17,
               'Gbm': 18, 'Gb': 19, 'Db': 20, 'Fm': 21, 'Ebm': 22, 'Bbm': 23, 'None': 24}

id_to_chord = {y: x for x, y in chord_to_id.items()}