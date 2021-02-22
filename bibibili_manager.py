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
    def __init__(self, uid, live_id, download_script_repo_path, repo_path, mode):
        self.mode = mode

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
        if self.mode == 1:
            self.lrDownloader.main()
        elif self.mode == 2:
            self.crDownloader.main()
        elif self.mode == 3:
            self.crDownloader.main()
            self.lrDownloader.main()


def main():
    YDDXMGJ = BilibiliManager(uid=9035182, live_id=3509872,
                              download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                              repo_path=r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official', mode=3)
    YDDXMGJ.main()
    YYXST = BilibiliManager(uid=358629230, live_id=13328782,
                            download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                            repo_path=r'/media/pi/sda1/media/bilibili_record/13328782-圆圆小石头-official', mode=2)
    YYXST.main()


if __name__ == '__main__':
    main()
