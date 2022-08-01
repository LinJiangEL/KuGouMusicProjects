import os
import re
import json
import requests
from typing import List, Dict
from fake_useragent import UserAgent
from prettytable import PrettyTable

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "cookie": "kg_mid=da93c5a16353e2dcfe4823d8e6f3f597; kg_dfid=2mSRIP0WnAKg0WbF83440A68; "
              "kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e",
    "User-Agent": UserAgent().random
}


def search(fullquery: str) -> List:
    search: str = fullquery if len(fullquery) <= 10 else fullquery[:11]
    pagesize = "10"
    url = 'https://songsearch.kugou.com/song_search_v2?' \
          'callback=jQuery11240251602301830425_1548735800928&' \
          'keyword=%s&' \
          'page=1&' \
          'pagesize=%s&' \
          'userid=-1&' \
          'clientver=&' \
          'platform=WebFilter&' \
          'tag=em&' \
          'filter=2&' \
          'iscorrection=1&' \
          'privilege_filter=0&' \
          '_=1548735800930' % (search, pagesize)
    res = json.loads(re.match(".*?({.*}).*", requests.get(url, headers=headers).text, re.S).group(1))

    list1 = res['data']['lists']
    musics: List[Dict[str, str]] = []

    for item in list1:
        url2 = 'https://wwwapi.kugou.com/yy/index.php?' \
               'r=play/getdata&' \
               'callback=jQuery191010559973368921649_1548736071852' \
               '&hash=%s&' \
               'album_id=%s&' \
               '_=1548736071853' % (item['FileHash'], item['AlbumID'])
        res2 = json.loads(re.match(".*?({.*}).*", requests.get(url2, headers=headers).text).group(1))['data']

        dict1 = {
            'author': res2['author_name'] if len(res2['author_name']) <= 10 else res2['author_name'][:11],
            'title': res2['song_name'] if len(res2['song_name']) <= 35 else res2['song_name'][:41],
            'id': str(res2['album_id']),
            'type': 'kugou',
            'pic': res2['img'],
            'url': res2['play_url'],
            'lrc': res2['lyrics']
        }

        if dict1.get("title") == "":
            continue
        else:
            musics.append(dict1)
    return musics


try:
    if not os.path.exists("musics"):
        os.mkdir("musics")

    while True:
        query: str = input("Please input MusicQuery: ")
        musicList = search(query)

        musicTable = PrettyTable(['序号', '歌曲名称', '歌手'])
        num = 0
        for i in musicList:
            musicTable.add_row([str(num + 1), i['title'].strip(), i['author'].strip()])
            num = num + 1

        print(musicTable)
        print("Please input the musicnum which you want to download.\nExample: 1,4,5\nInput: ", end="")
        musicChoice: List = input().split(',')
        for numd in musicChoice:
            try:
                numd: int = int(numd)
                if numd == 0:
                    continue
            except ValueError:
                print(f"Invalid Input on {numd}!")
                continue

            musicname: str = musicList[numd - 1].get("title")
            musicauthor: str = musicList[numd - 1].get("author")
            musicurl:str = musicList[numd - 1].get("url")

            print(f"\nMusic Information:\nTitle:{musicname}\nAuthor:{musicauthor}\nURL:{musicurl}\n")
            get_music = requests.get(musicurl)
            if get_music.status_code == 200:
                with open(f"musics/{musicname.strip()} - {musicauthor.strip()}.mp3", "wb") as musicfile:
                    musicfile.write(get_music.content)
                    print(f"Successfully download {musicname}&{musicauthor}!\n")
            else:
                print(f"Return {get_music.status_code} Error!")
except KeyboardInterrupt:
    print("SystemInfo:user cancelled the operation.")
    input('Please press Enter to exit.')
