import json

from settings.constants import *

##################################################################
################ CHORD CONSTANTS
##################################################################

try:
    with open(os.path.join(project_folder, "web_scraping/chord_frequencies_and_transitions_full.json"), 'r') as fp:
        chord_and_transition_dict = json.load(fp)

except FileNotFoundError:
    print("No chord frequencies or transitions exists. Please make sure to create such a file "
          "and save it at 'web_scraping/chord_frequencies_and_transitions_full.json'")
    raise FileNotFoundError
