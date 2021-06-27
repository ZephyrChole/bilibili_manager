# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: download.py
# @time: 2/20/2021 1:00 PM
import logging
import os
import xlrd
import xlwt
from bilibili_api import user
from BilibiliManager.custom_record import CustomRecordDownloader
from BilibiliManager.live_record import LiveRecordDownloader
from BilibiliManager.public import check_path, get_file_logger


class Downloader:
    logger = get_file_logger(logging.DEBUG, 'main')

    def __init__(self, download_script_repo, settings, upper_repo):
        self.download_script_repo = os.path.abspath(download_script_repo)
        self.setting_path = os.path.abspath(settings)
        self.upper_repo = os.path.abspath(upper_repo)

    def main(self):
        self.logger.debug(f'pid:{os.getpid()}')
        if self.check_settings():
            self.logger.info('有配置文件，开始运行')
            for info in self.get_info(self.setting_path):
                UPTask(self.download_script_repo, self.logger, self.upper_repo, info).main()
            self.logger.info('成功！ 等待下一次唤醒...')
        else:
            self.logger.info('无配置文件，初始化后退出。。。')
            self.init_setting()

    def check_settings(self):
        return os.path.exists(self.setting_path)

    def get_info(self, file_path):
        file = xlrd.open_workbook(file_path)
        sheet = file.sheet_by_index(0)
        raw_infos = [sheet.row_values(r) for r in range(sheet.nrows)]
        infos = list(map(lambda info: {raw_infos[0][i]: info[i] for i in range(len(info))}, raw_infos[1:]))
        return infos

    def init_setting(self):
        self.save([['uid', 'live', 'custom']])

    def save(self, data):
        file = xlwt.Workbook()
        sheet = file.add_sheet('BilibiliUP')
        for j in range(len(data)):
            for k in range(len(data[j])):
                sheet.write(j, k, data[j][k])
        file.save(self.setting_path)
        self.logger.info('up info saved')


class UPTask:
    def __init__(self, download_script_repo, logger, upper_repo, info):
        self.download_script_repo = download_script_repo
        self.live = info.get('live')
        self.custom = info.get('custom')
        self.up = UP(info.get('uid'))
        self.repo = os.path.join(upper_repo, '{}-{}'.format(self.up.uid, self.up.name))
        self.logger = logger

    def main(self):
        check_path('./log')
        self.logger.info(f'UP主:{self.up.name} uid:{self.up.uid} live_url:{self.up.live_url}')
        if self.custom:
            CustomRecordDownloader(self.download_script_repo, self.logger, self.repo, self.up).main()

        if self.live:
            LiveRecordDownloader(self.download_script_repo, self.logger, self.repo, self.up).main()


class UP:
    def __init__(self, uid):
        self.uid = int(uid)
        self.name = user.get_user_info(uid=self.uid).get('name')
        self.live_url = user.get_live_info(uid=self.uid).get('url')
