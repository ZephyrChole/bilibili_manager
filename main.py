# -*- coding: utf-8 -*-#

from custom_record import CustomRecordDownloader
# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2/20/2021 1:00 PM
from live_record import LiveRecordDownloader


def main():
    crDownloader = CustomRecordDownloader(9035182, r'E:\playground\from github\bili',
                                          r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_custom')
    lrDownloader = LiveRecordDownloader('3509872', r'E:\playground\from github\bili',
                                        r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_record')
    crDownloader.main()
    lrDownloader.main()


if __name__ == '__main__':
    main()
