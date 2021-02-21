# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2/20/2021 1:00 PM

import logging
import os

from custom_record import CustomRecordDownloader
from live_record import LiveRecordDownloader


def main():
    cur_path = '/home/pi/programs/bilibili_manager'
    os.chdir(cur_path)
    logger = logging.getLogger('LR')
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    LRDownloader = LiveRecordDownloader('3509872', r'E:\playground\from github\bili',
                                        r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_record', logger)
    LRDownloader.main()

    logger = logging.getLogger('CR')
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    crDownloader = CustomRecordDownloader(9035182, r'/media/pi/sda1/media/programs/bili',
                                          r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official/投稿视频', logger)
    crDownloader.main()


if __name__ == '__main__':
    main()
