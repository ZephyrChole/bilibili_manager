# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: daemon.py
# @time: 2/20/2021 1:54 PM
from BilibiliManager.download import Downloader

downloader = Downloader('./bili', './setting.xls', '/media/pi/sda1/media/bilibili_record')
downloader.main()
