# -*- coding: utf-8 -*-

import telebot
from config import TOKEN
import oss2
import requests
bot = telebot.TeleBot(TOKEN)
from expiringdict import ExpiringDict
import re
from Util import check_info
cache = ExpiringDict(max_len=100, max_age_seconds=60)
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
            + "5. setpath image_path_on_aliyunOss(图片路径有效期1分钟)"
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
    bot.send_message(message.chat.id, 'AccessKeyId设置成功')


@bot.message_handler(commands=['setaks'])
def send_AKS(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key["aks"] = str(message.text).replace('/setaks', '').strip()
    else:
        key = dict()
        key["aks"] = str(message.text).replace('/setaks', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(message.chat.id, 'AccessKeySecret设置成功')


@bot.message_handler(commands=['setpath'])
def set_imagepath(message):
    image_path = str(message.text).replace('/setpath', '').strip()
    reg = "(?i).+?\\.(jpg|gif|bmp|png|jpeg)"
    ret = re.match(reg, image_path, flags=0)
    if ret is None:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='图片路径非法！')
        return
    cache[message.chat.id] = image_path
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='图片路径已设置，请在1分钟内上传图片!')


@bot.message_handler(commands=['setep'])
def set_endpoint(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key['ep'] = str(message.text).replace('/setep', '').strip()
    else:
        key = dict()
        key["ep"] = str(message.text).replace('/setep', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='endpoint设置成功')


@bot.message_handler(commands=['setbk'])
def set_endpoint(message):
    if message.chat.id in key_cache:
        key = key_cache[message.chat.id]
        key['bk'] = str(message.text).replace('/setbk', '').strip()
    else:
        key = dict()
        key["bk"] = str(message.text).replace('/setbk', '').strip()
        key_cache[message.chat.id] = key
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='bucket设置成功')


@bot.message_handler(content_types=['photo'])
def upload_photo(message):
    info = check_info(key_cache, message.chat.id)
    if info is not None:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=info)
        return
    file_name = cache.get(message.chat.id)
    if file_name is None:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='请先设置图片上传路径(包括图片名称及后缀)!')
        return

    key = key_cache[message.chat.id]
    auth = oss2.Auth(key['aki'], key['aks'])

    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, key['ep'], key['bk'])
    # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    photo_info = bot.get_file(message.photo[-1].file_id)
    photo = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, photo_info.file_path))
    try:
        bucket.put_object(file_name, photo)
        bucket.put_object_acl(file_name, oss2.OBJECT_ACL_PUBLIC_READ)
        tmp = key['ep'].replace('https://', '').replace('http://', '')
        url = "https://"+key['bk']+"."+tmp+"/"+file_name
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=url)
    except oss2.exceptions.ServerError as e:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='请检查oss配置是否正确')


if __name__ == '__main__':
    bot.polling()


# 对配置持久化保存
# 代码Review
# 图片批量上传