# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: bibibili_manager.py
# @time: 2/20/2021 1:00 PM

import logging
import os
import time
from re import findall
from bilibili_api import user
from custom_record import CustomRecordDownloader
from live_record import LiveRecordDownloader


class UP:
    def __init__(self, uid):
        self.uid = int(uid)
        self.name = user.get_user_info(uid=self.uid).get('name')
        self.live_url = user.get_live_info(uid=self.uid).get('url')


class BilibiliManager:
    cr_folder = 'custom_record'
    lr_folder = 'live_record'

    def __init__(self, download_script_repo_path, uid, upper_repo_path, live, custom):
        self.download_script_repo_path = download_script_repo_path
        self.live = live
        self.custom = custom
        self.up = UP(uid)
        self.repo_path = os.path.join(upper_repo_path, '{}-{}'.format(self.up.uid, self.up.name))
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
        self.crLogger = self.get_logger(logging.INFO, 'custom_record')
        self.lrLogger = self.get_logger(logging.INFO, 'live_record')
        self.crDownloader = CustomRecordDownloader(download_script_repo_path=self.download_script_repo_path,
                                                   repo_path=os.path.join(self.repo_path, self.cr_folder),
                                                   logger=self.crLogger, up=self.up)
        self.lrDownloader = LiveRecordDownloader(download_script_repo_path=self.download_script_repo_path,
                                                 repo_path=os.path.join(self.repo_path, self.lr_folder),
                                                 logger=self.lrLogger, up=self.up)

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

    def clear_tem_download(self):
        for i in os.listdir(os.path.join(self.download_script_repo_path, 'Download')):
            ipath = os.path.join(os.path.join(self.download_script_repo_path, 'Download', i))
            if os.path.isfile(ipath):
                os.system('rm "{}"'.format(ipath))

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
        if self.live:
            self.start_lr_main()
        if self.custom:
            self.start_cr_main()
