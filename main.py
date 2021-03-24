# coding=utf-8
# author        : claws
# date          : 2021/3/22
# description   : tgbot

import configparser
import logging

import telegram
from flask import Flask, request
from flask_apscheduler import APScheduler
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater, CommandHandler, CallbackContext
from queue import Queue
import os
import random
import shutil

from nlp.olami import Olami
from pixiv.spider import Ranking
from picture.downloader import Downloader
from mnist.predict import PredictService

welcome_msg = '''
/help 查看功能
powered by python
'''

help_msg = '''
/pixiv 获得若干pixiv月榜图
发送贴图 返回图片
发送消息 聊天机器人伺候
发送图片 手写数字识别

以下为管理员命令：
/update 手动更新pixiv缓存'''

SIZE_LIMIT = 1024 * 1024 * 5
PIXIV_SEND_NUMBER = 6
ADMIN_ID = 767845024

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': '__main__:update_spider',  # 方法名
            # 'args': (1,2), # 入参
            'trigger': 'cron',  # interval表示循环任务
            'hour': 0,
        }
    ]


def update_spider():
    global ranking
    ranking.update()
    shutil.rmtree('pixiv_downloads')
    os.mkdir('pixiv_downloads')
    logger.info('audo update pixiv successed!')


# Initial Flask app
app = Flask(__name__)
app.config.from_object(Config())

# Initial bot by Telegram access token
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))


@app.route('/hook', methods=['POST'])
def webhook():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        # print(update.message.text)
        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'




def start_handler(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(welcome_msg)


def help_handler(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(help_msg)


olami = Olami()

def reply_handler(update: telegram.Update, context: CallbackContext):
    """Reply message."""
    text = update.message.text
    user_id = update.message.from_user.id
    reply = olami.nli(text, user_id)
    update.message.reply_text(reply)


downloader = Downloader()

predictor = PredictService()

def photo_handler(update, context):
    """处理图片消息"""
    # uid = update.message.from_user.id
    # if uid == ADMIN_ID:
    #     file = downloader.download_photo(update.message)
    #     res = predictor.predict(file)
    #     update.message.reply_text(file+'已下载')
    #     update.message.reply_text(res)
    #     os.remove(file)
    # else:
    #     update.message.reply_text("听不见！")
    file = downloader.download_photo(update.message)
    print(file)
    res = predictor.predict(file)
    # update.message.reply_text(file + '已下载')
    update.message.reply_text(str(res))
    os.remove(file)


def sticker_handler(update :telegram.Update, context):
    """处理贴图消息，以图片形式返回贴图"""
    file = downloader.download_sticker(update.message)
    update.message.reply_photo(open(file, 'rb'))
    os.remove(file)



ranking = Ranking(mode='monthly')


def pixiv_handler(update: telegram.Update, context):
    """返回pixiv日榜图片"""
    download_tip: telegram.Message = update.message.reply_text("下载中，请稍候")
    # update.message.reply_photo(open('pixiv_downloads/88588799_p0.jpg','rb'))
    photos = []
    i = 0
    while i < PIXIV_SEND_NUMBER:
        pic = ranking.get_pic()
        fsize = os.path.getsize(pic)
        if fsize > SIZE_LIMIT:
            # logger.info('over size limit ==> ' + pic)
            continue
        photos.append(telegram.InputMediaPhoto(open(pic, 'rb')))
        # logger.info('send ==> ' + pic)
        i += 1
    # update.message.reply_photo(open(ranking.get_pic(), 'rb'))
    update.message.reply_media_group(photos)
    download_tip.delete()


def pixiv_update_handler(update: telegram.Update, context):
    uid = update.message.from_user.id
    if uid == ADMIN_ID:
        update_spider()
        update.message.reply_text("排行榜已更新！")
    else:
        update.message.reply_text("听不见！")


def error_handler(update, error):
    """Log Errors caused by Updates."""
    logger.error('Update \n"%s" \ncaused error \n"%s"', update, error)
    update.message.reply_text("我炸了qwq")


# New a dispatcher for bot
update_queue = Queue()
dispatcher = Dispatcher(bot, update_queue=update_queue)
# dispatcher = Dispatcher(bot, update_queue)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('pixiv', pixiv_handler))
dispatcher.add_handler(CommandHandler('update', pixiv_update_handler))
dispatcher.add_handler(MessageHandler(Filters.sticker, sticker_handler))
dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
# dispatcher.add_error_handler(error_handler)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    # Running server
    app.run(debug=True)
    # print(ranking.get_pic())
