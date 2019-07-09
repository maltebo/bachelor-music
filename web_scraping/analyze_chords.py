import json
import os
import random
import re
import time
import traceback
import urllib

from bs4 import BeautifulSoup

import settings.constants as c

with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings2.json"), 'r') as fp:
    urls = json.load(fp)

i = 0

tonality_set = set()
chords_set = set()
with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'r') as fp:
    urls_and_chords = json.load(fp)
    urls_visited = set(urls_and_chords.keys())

print(len(urls_visited))

for url in urls:

    if url in urls_visited:
        continue

    print("Opening", url)

    try:

        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")
        print("...successful")
    except urllib.error.HTTPError:
        print("...failed with HTTPError")
        traceback.print_exc()
        with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'w') as fb:
            fb.write(json.dumps(urls_and_chords))
        break

    except urllib.error.URLError:
        print("... failed with URLError")
        traceback.print_exc()
        with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'w') as fb:
            fb.write(json.dumps(urls_and_chords))
        continue

    except:
        print("...failed")
        traceback.print_exc()
        with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'w') as fb:
            fb.write(json.dumps(urls_and_chords))
        break

    body = soup.find('body')

    scripts = body.find_all('script')

    result = None

    for s in scripts:
        result = str(s).split("\n")[1]
        if re.match(r"\s*window\.UGAPP\.store\.page", result):
            break

    if not result:
        print("Did not find a data entry")
        continue

    json_data = ' = '.join(result.split(' = ')[1:])[0:-1]  # ends with ;

    tonality_pattern = r"\"tonality_name\":\"(\w+)\""

    chords_pattern = r"(?:(?:\s|\\n|\\r)+(?:\[ch\][^\s]{1,10}\[\\\/ch\]\s*)+(?:\s|\\n|\\r)+[\w][\w,'?!. ]+)|(?:\s*(?:\[ch\][^\s]{1,10}\[\\\/ch\])\s*){3,}"
    single_chord_pattern = r"\[ch\]([^\s]{1,10})\[\\\/ch\]"

    try:
        last_idx = re.search("\"recording\"", json_data).start()
    except:
        print("No recording found")
        traceback.print_exc()
        continue

    tonality = re.search(tonality_pattern, json_data[:last_idx])
    if tonality:
        tonality_set.add(tonality.group(1))

    chords_lines = re.findall(chords_pattern, json_data)

    song_chords = []

    for line in chords_lines:
        chords_succession = re.findall(single_chord_pattern, line)
        for ch in chords_succession:
            # print(ch)
            chords_set.add(ch)
            if song_chords:
                if song_chords[-1] != ch:
                    song_chords.append(ch)
            else:
                song_chords.append(ch)

    urls_visited.add(url)
    if tonality:
        t = tonality.group(1)
    else:
        t = None
    urls_and_chords[url] = {"tonality": t, "chords": song_chords}

    i += 1
    # break
    if i % 1 == 0:
        time.sleep(random.random() / 6)
        if random.random() < 0.05:
            time.sleep(1)
        print("Tonality Set", tonality_set)
        print("Chord Set", chords_set)
        with open(os.path.join(c.project_folder, "web_scraping/urls_and_chords.json"), 'w') as fb:
            fb.write(json.dumps(urls_and_chords))

print("finished everything!")

# A line with chords above:
# \s+

# page_nr = 1
#
# while page_nr <= 20:
#
#     print("Loading page {}".format(page_nr))
#
#     response = urllib.request.urlopen('https://www.ultimate-guitar.com/explore?genres[]=14&order=rating_desc&page='
#                                       '{page_nr}&part[]=&type[]=Chords'.format(page_nr=page_nr))
#     html = response.read()
#     soup = BeautifulSoup(html, "lxml")
#
#     # print(soup)
#
#     table = soup.find_all('script') # window.UGAPP.store.page = {"template":{"module":"search","controller":"explore","action":"index"},"data":{"pagination":{"pages":20,"curren
#
#     table_line = str(table[-3]).split("\n")[1]
#
#     json_data = table_line.split(' = ')[-1][0:-1] # ends with ;
#
#     print(json_data)
#
#     import json
#
#     json_dict = json.loads(json_data)
#     important_data = json_dict["data"]["data"]["tabs"]
#
#     # print(json.dumps(important_data, indent=2))
#
#     for song in important_data:
#         if float(song["rating"]) < 4.5:
#             continue
#         urls.append(song["tab_url"])
#
#     page_nr += 1
#
# print(json.dumps(urls, indent=2))
#
