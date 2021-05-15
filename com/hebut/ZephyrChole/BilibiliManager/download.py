# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: download.py
# @time: 2/20/2021 1:00 PM

import os
import time
import logging
from bilibili_api import user
from com.hebut.ZephyrChole.BilibiliManager.custom_record import CustomRecordDownloader
from com.hebut.ZephyrChole.BilibiliManager.live_record import LiveRecordDownloader
from com.hebut.ZephyrChole.BilibiliManager.public import check_path


class UP:
    def __init__(self, uid):
        self.uid = int(uid)
        self.name = user.get_user_info(uid=self.uid).get('name')
        self.live_url = user.get_live_info(uid=self.uid).get('url')


class Downloader:
    cr_folder = 'custom_record'
    lr_folder = 'live_record'

    def __init__(self, download_script_repo, upper_repo, uid, live, custom):
        self.download_script_repo = download_script_repo
        self.live = live
        self.custom = custom
        self.up = UP(uid)
        self.repo = os.path.join(upper_repo, '{}-{}'.format(self.up.uid, self.up.name))
        self.init_downloader()

    @staticmethod
    def get_logger(level, name):
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('./log/{}.log'.format(time.strftime("%Y-%m-%d", time.localtime())),
                                 encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(fh)
        return logger

    def init_downloader(self):
        check_path('./log')
        self.crLogger = self.get_logger(logging.INFO, 'custom_record')
        self.lrLogger = self.get_logger(logging.INFO, 'live_record')
        self.crDownloader = CustomRecordDownloader(download_script_repo=self.download_script_repo,
                                                   repo=os.path.join(self.repo, self.cr_folder),
                                                   logger=self.crLogger, up=self.up)
        self.lrDownloader = LiveRecordDownloader(download_script_repo=self.download_script_repo,
                                                 repo=os.path.join(self.repo, self.lr_folder),
                                                 logger=self.lrLogger, up=self.up)

    def start_lr_main(self):
        if check_path(os.path.join(self.repo, self.lr_folder)):
            self.lrLogger.info('live record path check success')
            self.lrDownloader.main()
        else:
            self.lrLogger.info('live record path check fail')

    def start_cr_main(self):
        if check_path(os.path.join(self.repo, self.cr_folder)):
            self.crLogger.info('custom record path check success')
            self.crDownloader.main()
        else:
            self.crLogger.info('custom record path check fail')

    def main(self):
        if self.live:
            self.start_lr_main()
        if self.custom:
            self.start_cr_main()
