import re
import json
import requests
from fake_useragent import UserAgent
from prettytable import PrettyTable

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "cookie": "kg_mid=da93c5a16353e2dcfe4823d8e6f3f597; kg_dfid=2mSRIP0WnAKg0WbF83440A68; "
              "kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e",
    "User-Agent": UserAgent().random
}

# 请求搜索列表数据
fullquery = input('音乐名:')  # 控制台输入搜索关键词
search = fullquery if len(fullquery) <= 10 else fullquery[:11]
pagesize = "10"  # 请求数目
url = 'https://songsearch.kugou.com/song_search_v2?callback=jQuery11240251602301830425_1548735800928&keyword=%s&page' \
      '=1&pagesize=%s&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_' \
      '=1548735800930' % (search, pagesize)
res = requests.get(url, headers=headers)  # 进行get请求

# 需要注意一点，返回的数据并不是真正的json格式，前后有那个多余字符串需要用正则表达式去掉,只要大括号{}包着的内容
# json.loads就是将json数据转为python字典的函数
res = json.loads(re.match(".*?({.*}).*", res.text, re.S).group(1))

list1 = res['data']['lists']  # 这个就是歌曲列表

# 建立List存放歌曲列表信息，将这个歌曲列表输出，别的程序就可以直接调用
musicList = []

# for循环遍历列表得到每首单曲的信息
for item in list1:
    # 将列表每项的item['FileHash'],item['AlbumID']拼接请求url2
    url2 = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery191010559973368921649_1548736071852' \
           '&hash=%s&album_id=%s&_=1548736071853' % (item['FileHash'], item['AlbumID'])
    res2 = json.loads(re.match(".*?({.*}).*", requests.get(url2, headers=headers).text).group(1)) \
           ['data']  # 同样需要用正则处理一下才为json格式,再转为字典

    # 打印一下
    # print('---------------------------------------------')
    # print(res2['song_name'] + ' - ' + res2['author_name'])
    # print(res2['play_url'])
    # print('---------------------------------------------')
    # print('')

    # 将单曲信息存在一个字典里
    dict1 = {
        'author': res2['author_name'] if len(res2['author_name']) <= 8 else res2['author_name'][:8],
        'title': res2['song_name'] if len(res2['song_name']) <= 35 else res2['song_name'][:35],
        'id': str(res2['album_id']),
        'type': 'kugou',
        'pic': res2['img'],
        'url': res2['play_url'],
        'lrc': res2['lyrics']
    }

    # 将字典添加到歌曲列表
    musicList.append(dict1)

musicTable = PrettyTable(['序号', '歌曲名称', '歌手'])
num = 0
for i in musicList:
    musicTable.add_row([str(num+1), i['title'].strip(), i['author'].strip()])
    num = num + 1

print(musicTable)
input('Over.')
