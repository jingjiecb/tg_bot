# coding=utf-8
# author        : claws
# date          : 2021/3/24
# description   : download pic
import configparser
import os

import telegram

# from  telegram.ext import Update
import requests

config = configparser.ConfigParser()
config.read('config.ini')

BOT_TOKEN = config['TELEGRAM']['ACCESS_TOKEN']


class Downloader:

    def __init__(self, dst_path='picture_downloads/'):
        self.dst_path = dst_path

    def download_photo(self, message, quality=0):
        """quality 0 差 1 中 2  高"""

        file_id = message.photo[quality].file_id
        # Get file_path
        # photo = self.get_json('getFile', params={"file_id": file_id})
        photo_url = "https://api.telegram.org/bot{}/getFile?file_id={}".format(BOT_TOKEN, file_id)
        photo = requests.get(photo_url).json()
        file_path = photo['result']['file_path']
        # Download photo
        file_name = os.path.basename(file_path)
        response = requests.get('https://api.telegram.org/file/bot%s/%s' % (BOT_TOKEN, file_path))
        dst_file_path = os.path.join(self.dst_path, file_name)
        with open(dst_file_path, 'wb') as f:
            f.write(response.content)
        print(u"Downloaded file to {}".format(dst_file_path))

        return dst_file_path

    def download_sticker(self, message):

        file_id = message.sticker.file_id
        # Get file_path
        # photo = self.get_json('getFile', params={"file_id": file_id})
        photo_url = "https://api.telegram.org/bot{}/getFile?file_id={}".format(BOT_TOKEN, file_id)
        photo = requests.get(photo_url).json()
        file_path = photo['result']['file_path']
        # Download photo
        file_name = os.path.basename(file_path)
        response = requests.get('https://api.telegram.org/file/bot%s/%s' % (BOT_TOKEN, file_path))
        dst_file_path = os.path.join(self.dst_path, file_name)
        with open(dst_file_path, 'wb') as f:
            f.write(response.content)
        print(u"Downloaded file to {}".format(dst_file_path))

        return dst_file_path



    # def get_json(self, method_name, *args, **kwargs):
    #     return self.make_request('get', method_name, *args, **kwargs)
    #
    # def make_request(self, method, method_name, *args, **kwargs):
    #     response = getattr(requests, method)(
    #         'https://api.telegram.org/bot%s/%s' % (BOT_TOKEN, method_name),
    #         *args, **kwargs
    #     )
    #     if response.status_code > 200:
    #         raise DownloadError(response)
    #     return response.json()

# class DownloadError(Exception):
#     pass
