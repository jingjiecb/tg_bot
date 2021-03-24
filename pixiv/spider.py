# coding=utf-8
# author        : claws
# date          : 2021/3/23
# description   : pixiv_spider

# -*-coding:utf-8-*-
import requests
import json
import re
import os

# 请求参数
# 代理
# proxies = {"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809", }
header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    'Referer': "https://www.pixiv.net/"
}

save_path = './downloads/'
base_url = "https://www.pixiv.net/artworks/"
ranking_url = "https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%d&format=json"
original_download_url_pattern = re.compile('"original":"(.*?)"', re.S)
regular_download_url_pattern = re.compile('"regular":"(.*?)"', re.S)
pic_name_pattern = re.compile(r'/(\d+_p\d+.*?\..*)$')


def save_to_file(filepath, purl):
    with open(filepath, 'wb') as f:
        # imgC = requests.get(purl, proxies=proxies, headers=header).content
        imgC = requests.get(purl, headers=header).content
        f.write(imgC)


def get_part_ranking_urls(url, quality='regular'):
    # 访问排行榜
    # raw_json = requests.get(url, proxies=proxies, headers=header).content
    raw_json = requests.get(url, headers=header).content
    data = json.loads(raw_json)

    for picture in data["contents"]:
        pid = str(picture["illust_id"])
        page = picture["illust_page_count"]

        # 访问每份图片具体的网页
        purl = base_url + pid
        # html = requests.get(purl, proxies=proxies, headers=header).text
        html = requests.get(purl, headers=header).text

        if quality == 'regular':
            first_download_url = regular_download_url_pattern.search(html).group(1)
        elif quality == 'original':
            first_download_url = original_download_url_pattern.search(html).group(1)
        else:
            first_download_url = regular_download_url_pattern.search(html).group(1)
        # download_urls=[first_download_url]

        # 下载每套图片下的所有图片
        for i in range(int(page)):
            pic_download_url = re.sub(r'(?<=_p)\d+', str(i), first_download_url)
            # print(pic_download_url)
            file_name = pic_name_pattern.search(pic_download_url).group(1)
            yield {
                'file_name': file_name,
                'url': pic_download_url
            }


# def download_ranking_pictures():
#     for i in range(1, 2):
#         pics = get_part_ranking_urls(ranking_url % (i))
#         for pic in pics:
#             print("INFO | downloading {} ", pic['file_name'])
#             save_to_file(pic['file_name'], pic['url'])

class Ranking:
    def __init__(self, mode='daily', quality='regular'):
        self.page = 1
        self.quality = quality
        if mode == 'daily':
            self.ranking_url = "https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%d&format=json"
        elif mode == 'monthly':
            self.ranking_url = "https://www.pixiv.net/ranking.php?mode=monthly&content=illust&p=%d&format=json"
        else:
            self.ranking_url = "https://www.pixiv.net/ranking.php?mode=monthly&content=illust&p=%d&format=json"
        # if mode == 'daily_r18':
        #     self.ranking_url = "https://www.pixiv.net/ranking.php?mode=daily_r18&content=illust&p=%d&format=json"
        self.rank = get_part_ranking_urls(self.ranking_url % (self.page), self.quality)

    def get_pic(self):
        try:
            pic = next(self.rank)
        except StopIteration as e:
            self.page += 1
            self.page %= 10
            self.rank = get_part_ranking_urls(self.ranking_url % (self.page), self.quality)
            pic = next(self.rank)

        file, url = 'pixiv_downloads/{0}'.format(pic['file_name']), pic['url']
        if not os.path.exists(file):
            # print("download : " + file)
            save_to_file(file, url)
        # else:
        #     print("existed : " + file)
        return file

    def save_to_file(self, filepath, purl):
        with open(filepath, 'wb') as f:
            imgC = requests.get(purl, headers=header).content
            # imgC = requests.get(purl, proxies=proxies, headers=header).content
            f.write(imgC)

    def update(self):
        self.page = 1
        self.rank = get_part_ranking_urls(self.ranking_url % (self.page), self.quality)


if __name__ == "__main__":
    ranking = Ranking()
    print(ranking.get_pic())
