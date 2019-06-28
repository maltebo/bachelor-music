import json
import os
import urllib

from bs4 import BeautifulSoup

import settings.constants as c

subgenres = [
    24, 751, 665, 343, 734, 218, 192, 104, 46, 1095, 910, 36, 414, 1093, 197, 487, 150, 565, 140, 47, 103, 938, 177, 11,
    317, 296, 326, 9, 37, 707, 77, 179, 383, 259, 86, 94, 842, 318, 3, 75, 792, 202, 66, 82, 813, 323, 87, 704, 347, 12,
    170, 101, 18, 268, 1060, 1087, 1089, 236, 1015, 152, 915, 849, 431, 238, 69, 376, 795, 760, 191, 198, 267, 879, 427,
    668, 438, 1026, 167, 1, 30, 226, 1091, 809, 302, 703, 33, 1013, 139, 119, 777, 27, 106, 308, 736, 669, 404, 940,
    305, 56, 825, 138
]

decade = [1980, 1990, 2000, 2010]

try:
    with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings2.json"), "r") as fp:
        urls = set(json.load(fp))
except:
    with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings.json"), "r") as fp:
        urls = set(json.load(fp))
    with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings2.json"), "x") as fp:
        fp.write(json.dumps(list(urls), indent=2))

try:
    with open(os.path.join(c.project_folder, "web_scraping/pages_visited.json"), "r") as fp:
        pages_visited = set(json.load(fp))
except:
    pages_visited = set()
    with open(os.path.join(c.project_folder, "web_scraping/pages_visited.json"), "x") as fp:
        fp.write(json.dumps(list(pages_visited), indent=2))

print(urls)

weird = False

for sub in subgenres:

    for dec in decade:

        valid = True

        page_nr = 1

        while valid and page_nr <= 20:

            page_name = ('https://www.ultimate-guitar.com/explore?decade[]={dec}&genres[]=14&'
                         'order=rating_desc&page={page_nr}&part[]=&subgenres[]={sub}&'
                         'type[]=Chords'.format(dec=dec,
                                                page_nr=page_nr,
                                                sub=sub))

            try:
                if page_name in pages_visited:
                    break
                print(page_name)
                response = urllib.request.urlopen(page_name)
                pages_visited.add(page_name)
            except urllib.error.HTTPError:
                pages_visited.add(page_name)
                break
            except:
                weird = True
                break

            html = response.read()
            soup = BeautifulSoup(html, "lxml")

            table = soup.find_all('script')

            table_line = str(table[-3]).split("\n")[1]

            json_data = table_line.split(' = ')[-1][0:-1]  # ends with ;

            # print(json_data)

            json_dict = json.loads(json_data)
            important_data = json_dict["data"]["data"]["tabs"]

            # print(json.dumps(important_data, indent=2))

            for song in important_data:
                if int(song["votes"]) < 5:
                    valid = False
                    continue
                if float(song["rating"]) < 4.5:
                    continue
                urls.add(song["tab_url"])

                if len(urls) % 10 == 0:
                    with open(os.path.join(c.project_folder, "web_scraping/pages_visited.json"), "w") as fp:
                        fp.write(json.dumps(list(pages_visited), indent=2))

                    with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings2.json"),
                              "w") as fp:
                        fp.write(json.dumps(list(urls), indent=2))

            page_nr += 1

        if weird:
            break
    if weird:
        break

with open(os.path.join(c.project_folder, "web_scraping/pages_visited.json"), "w") as fp:
    fp.write(json.dumps(list(pages_visited), indent=2))

with open(os.path.join(c.project_folder, "web_scraping/urls_for_chord_embeddings2.json"), "w") as fp:
    fp.write(json.dumps(list(urls), indent=2))
