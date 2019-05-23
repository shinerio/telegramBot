# -*- coding: utf-8 -*-

import telebot
import requests
from config import TOKEN
bot = telebot.TeleBot(TOKEN)
import re
from util import check_info, upload_image
import yaml
key_cache = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, '阿里云oss上传工具')


@bot.message_handler(commands=['help'])
def send_help(message):
    help = "阿里云oss文件长传工具\n使用本工具请首先访问阿里云控制台获取accessKeys,使用set指令进行config配置\n" \
            + "------------------------------------------------------------------------------\n"\
            + "1. setbk yourbucket\n"\
            + "2. setep yourendpoint\n"\
            + "3. setaki yourAccessKeyId\n"\
            + "4. setaks yourAccessKeySecret\n"\
            + "5. setpath image_path_on_aliyunOss"
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=help)


@bot.message_handler(commands=['setaki'])
def set_AKI(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key["aki"] = str(message.text).replace('/setaki', '').strip()
    else:
        key = dict()
        key["aki"] = str(message.text).replace('/setaki', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(message.chat.id, 'AccessKeyId设置成功!')


@bot.message_handler(commands=['setaks'])
def send_AKS(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key["aks"] = str(message.text).replace('/setaks', '').strip()
    else:
        key = dict()
        key["aks"] = str(message.text).replace('/setaks', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(message.chat.id, 'AccessKeySecret设置成功!')


@bot.message_handler(commands=['setpath'])
def set_imagepath(message):
    image_path = str(message.text).replace('/setpath', '').strip()
    if image_path.startswith("/"):
        image_path = image_path[1:]
    if image_path.endswith("/"):
        image_path = image_path[:-1]
    ret = check_info(key_cache, message.chat.id)
    if ret is not None:  # oss error
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=ret)
        return
    else:
        key_cache[message.chat.id]["path"] = image_path
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='图片路径已切换!')


@bot.message_handler(commands=['setep'])
def set_endpoint(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key['ep'] = str(message.text).replace('/setep', '').strip()
    else:
        key = dict()
        key["ep"] = str(message.text).replace('/setep', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='endpoint设置成功!')


@bot.message_handler(commands=['setbk'])
def set_endpoint(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key['bk'] = str(message.text).replace('/setbk', '').strip()
    else:
        key = dict()
        key["bk"] = str(message.text).replace('/setbk', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='bucket设置成功!')


@bot.message_handler(content_types=['document'])
def deploy_document(message):
    file_name = message.document.file_name.encode('utf-8')
    if file_name.endswith(".yaml"):
        document_info = bot.get_file(message.document.file_id)
        document = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, document_info.file_path))
        content = document.text.encode('utf-8')
        try:
            content = yaml.load(content)
        except:
            bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text="文件格式不正确!")
        for item in ['bucket', 'AccessKeySecret', 'AccessKeyId', 'endpoint']:
            if item not in content:
                bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=item+"未设置")
                return
        key = dict()
        key['bk'] = content['bucket']
        key['aks'] = content['AccessKeySecret']
        key['aki'] = content['AccessKeyId']
        key['ep'] = content['endpoint']
        key_cache[message.chat.id] = key
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text="oss配置成功")
        return

    reg = "(?i).+?\\.(jpg|gif|bmp|png|jpeg)"
    ret = re.match(reg, file_name, flags=0)
    if ret is not None:
        info = check_info(key_cache, message.chat.id)
        if info is not None:  # oss error
            bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=info)
            return
        else:  # upload image
            photo_info = bot.get_file(message.document.file_id)
            photo = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, photo_info.file_path))
            info = upload_image(key_cache, message, photo)
            bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=info)
    else:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text="文件格式不正确!")


@bot.message_handler(content_types=['photo'])
def upload_photo(message):
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text="请以文件方式进行上传")


if __name__ == '__main__':
    bot.polling()
