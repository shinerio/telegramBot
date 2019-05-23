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
    if "path" in key:
        file_name = key["path"]+"/"+file_name
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, key['ep'], key['bk'])
    # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
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
