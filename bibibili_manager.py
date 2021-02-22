# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: bibibili_manager.py
# @time: 2/20/2021 1:00 PM

import logging
import os

from custom_record import CustomRecordDownloader
from live_record import LiveRecordDownloader


class BilibiliManager:
    def __init__(self, uid, live_id, download_script_repo_path, repo_path):
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        crLogger = logging.getLogger('CR')
        crLogger.setLevel(logging.INFO)
        crLogger.addHandler(ch)

        lrLogger = logging.getLogger('LR')
        lrLogger.setLevel(logging.INFO)
        lrLogger.addHandler(ch)

        self.crDownloader = CustomRecordDownloader(uid=uid, download_script_repo_path=download_script_repo_path,
                                                   repo_path=os.path.join(repo_path, 'custom_record'), logger=crLogger)
        self.lrDownloader = LiveRecordDownloader(live_id=live_id, download_script_repo_path=download_script_repo_path,
                                                 repo_path=os.path.join(repo_path, 'live_record'), logger=lrLogger)

    def main(self):
        self.crDownloader.main()
        self.lrDownloader.main()


def main():
    bilibili_manager = BilibiliManager(uid=9035182, live_id=3509872,
                                       download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                                       repo_path=r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official')
    bilibili_manager.main()


if __name__ == '__main__':
    main()
