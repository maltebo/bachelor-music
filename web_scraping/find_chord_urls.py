import json
import urllib

from bs4 import BeautifulSoup

urls = []

page_nr = 1

while page_nr <= 20:

    print("Loading page {}".format(page_nr))

    response = urllib.request.urlopen('https://www.ultimate-guitar.com/explore?genres[]=14&order=rating_desc&page='
                                      '{page_nr}&part[]=&type[]=Chords'.format(page_nr=page_nr))
    html = response.read()
    soup = BeautifulSoup(html, "lxml")

    # print(soup)

    table = soup.find_all(
        'script')  # window.UGAPP.store.page = {"template":{"module":"search","controller":"explore","action":"index"},"data":{"pagination":{"pages":20,"curren

    table_line = str(table[-3]).split("\n")[1]

    json_data = table_line.split(' = ')[-1][0:-1]  # ends with ;

    print(json_data)

    json_dict = json.loads(json_data)
    important_data = json_dict["data"]["data"]["tabs"]

    # print(json.dumps(important_data, indent=2))

    for song in important_data:
        if float(song["rating"]) < 4.5:
            continue
        urls.append(song["tab_url"])

    page_nr += 1

print(json.dumps(urls, indent=2))
