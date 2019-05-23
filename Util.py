# -*- coding: utf-8 -*-


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