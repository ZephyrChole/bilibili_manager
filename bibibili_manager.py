# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: bibibili_manager.py
# @time: 2/20/2021 1:00 PM

import logging
import os
from re import findall

from custom_record import CustomRecordDownloader
from live_record import LiveRecordDownloader


class BilibiliManager:
    cr_folder = 'custom_record'
    lr_folder = 'live_record'

    def __init__(self, uid, live_id, download_script_repo_path, repo_path, mode):
        self.mode = mode
        self.repo_path = repo_path

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        self.crLogger = logging.getLogger('CR')
        self.crLogger.setLevel(logging.INFO)
        self.crLogger.addHandler(ch)

        self.lrLogger = logging.getLogger('LR')
        self.lrLogger.setLevel(logging.INFO)
        self.lrLogger.addHandler(ch)

        self.crDownloader = CustomRecordDownloader(uid=uid, download_script_repo_path=download_script_repo_path,
                                                   repo_path=os.path.join(repo_path, self.cr_folder),
                                                   logger=self.crLogger)
        self.lrDownloader = LiveRecordDownloader(live_id=live_id, download_script_repo_path=download_script_repo_path,
                                                 repo_path=os.path.join(repo_path, self.lr_folder),
                                                 logger=self.lrLogger)

    @staticmethod
    def init_path(path):
        path_group = findall('/[^/]+', path)
        try:
            for i in range(1, len(path_group) + 1):
                tem_path = ''.join(path_group[0:i])
                if not os.path.exists(tem_path):
                    os.mkdir(tem_path)
            return True
        except:
            return False

    def start_lr_main(self):
        if self.init_path(os.path.join(self.repo_path, self.lr_folder)):
            self.lrLogger.info('live record path check success')
            self.lrDownloader.main()
        else:
            self.lrLogger.info('live record path check fail')

    def start_cr_main(self):
        if self.init_path(os.path.join(self.repo_path, self.cr_folder)):
            self.crLogger.info('custom record path check success')
            self.crDownloader.main()
        else:
            self.crLogger.info('custom record path check fail')

    def main(self):
        if self.mode == 1:
            self.start_lr_main()
        elif self.mode == 2:
            self.start_cr_main()
        elif self.mode == 3:
            self.start_cr_main()
            self.start_lr_main()


def main():
    YDDXMGJ = BilibiliManager(uid=9035182, live_id=3509872,
                              download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                              repo_path=r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official', mode=3)
    YDDXMGJ.main()
    YYXST = BilibiliManager(uid=358629230, live_id=13328782,
                            download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                            repo_path=r'/media/pi/sda1/media/bilibili_record/13328782-圆圆小石头-official', mode=2)
    YYXST.main()
    os.system('clear')


if __name__ == '__main__':
    main()
