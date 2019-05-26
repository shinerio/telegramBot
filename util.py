# -*- coding: utf-8 -*-

import oss2


def check_info(key_cache, chat_id):
    if chat_id not in key_cache:
        return "请先完成oss配置！"
    key = key_cache[chat_id]
    if "aks" not in key:
        return '请使用setaks配置AccessKeySecret'
    elif "aki" not in key:
        return '请使用setaki配置AccessKeyId'
    elif 'ep' not in key:
        return '请使用setepue设置endpoint'
    elif 'bk' not in key:
        return '请使用setbk设置bucket'
    return None


def upload_image(key_cache, message, photo):
    key = key_cache[message.chat.id]
    auth = oss2.Auth(key['aki'], key['aks'])
    file_name = message.document.file_name.encode('utf-8')
    if "name" in key:
        file_name = key["name"]
        del key["name"]
    if "path" in key and key["path"]!="":
        file_name = key["path"]+"/"+file_name
    bucket = oss2.Bucket(auth, key['ep'], key['bk'])
    try:
        exist = bucket.object_exists(file_name)
        if exist:
            return "同名文件已存在!"
        bucket.put_object(file_name, photo)
        bucket.put_object_acl(file_name, oss2.OBJECT_ACL_PUBLIC_READ)
        tmp = key['ep'].replace('https://', '').replace('http://', '')
        url = "https://" + key['bk'] + "." + tmp + "/" + file_name
        return url
    except oss2.exceptions.ServerError:
        return '请检查oss配置是否正确'


def get_dir(key_cache, message):
    ret = []
    key = key_cache[message.chat.id]
    auth = oss2.Auth(key['aki'], key['aks'])
    bucket = oss2.Bucket(auth, key['ep'], key['bk'])
    dir = message.text.encode('utf-8').replace('/list', '').strip()
    dir = None if dir == "" else dir
    try:
        for obj in oss2.ObjectIterator(bucket):
            if obj.key.endswith("/"):
                if dir is None:
                    ret.append(obj.key)
                elif obj.key.startswith(dir):
                    ret.append(obj.key)
        if len(ret) == 0:
            return "empty!"
        tmp=""
        for item in ret:
            tmp = tmp+item+"\n"
        return tmp
    except oss2.exceptions.ServerError:
        return '请检查oss配置是否正确'
