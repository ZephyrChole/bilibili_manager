# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: daemon.py
# @time: 2/20/2021 1:54 PM
from BilibiliManager.download import Downloader
import time

attempt = 0
while True:
    attempt += 1
    try:
        downloader = Downloader('./bili', './setting.xls', '/media/pi/sda1/media/bilibili_record')
        downloader.main()
        break
    except Exception as e:
        print(e)
        if attempt > 3:
            print('failed')
            break
        time.sleep(60 * 10)
