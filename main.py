# -*- coding: utf-8 -*-#

from custom_record import CustomRecordDownloader
# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2/20/2021 1:00 PM
from live_record import LiveRecordDownloader


def main():
    crDownloader = CustomRecordDownloader(9035182, r'/home/pi/programs/bili',
                                          r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official/投稿视频')
    lrDownloader = LiveRecordDownloader('3509872', r'/home/pi/programs/bili',
                                        r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official/直播回放')
    crDownloader.main()
    lrDownloader.main()


if __name__ == '__main__':
    main()
