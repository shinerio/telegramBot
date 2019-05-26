# telegramBot

aliyun oss文件小助手

## prerequisite

```
pip install expiringdict
pip install pyTelegramBotAPI
```

```
mv config_example.py config.py
update TOKEN to you telegrambot API token
nohup python main.py
```

## 支持功能

- 上传单张图片并返回网络地址

## 待更新

- [x] 上传config文件设置oss配置
- [x] 图片上传路径优化
- [x] 覆盖提醒
- [x] 图片改名
- [ ] 配置持久化
- [ ] 图片批量上传
- [x] 列出bucket目录选择上传路径
