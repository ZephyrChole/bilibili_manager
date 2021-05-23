# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: download.py
# @time: 2/20/2021 1:00 PM
import logging
import os
import xlrd
import xlwt
from com.hebut.ZephyrChole.BilibiliManager.public import get_abs
from bilibili_api import user
from com.hebut.ZephyrChole.BilibiliManager.custom_record import CustomRecordDownloader
from com.hebut.ZephyrChole.BilibiliManager.live_record import LiveRecordDownloader
from com.hebut.ZephyrChole.BilibiliManager.public import check_path, get_file_logger


class UP:
    def __init__(self, uid):
        self.uid = int(uid)
        self.name = user.get_user_info(uid=self.uid).get('name')
        self.live_url = user.get_live_info(uid=self.uid).get('url')


class Task:
    cr_folder = 'custom_record'
    lr_folder = 'live_record'

    def __init__(self, download_script_repo, upper_repo, uid, live, custom):
        self.download_script_repo = download_script_repo
        self.live = live
        self.custom = custom
        self.up = UP(uid)
        self.repo = os.path.join(upper_repo, '{}-{}'.format(self.up.uid, self.up.name))

    def main(self):
        check_path('./log')
        if self.custom:
            task = CustomRecordDownloader(download_script_repo=self.download_script_repo,
                                          repo=os.path.join(self.repo, self.cr_folder),
                                          up=self.up)
            self.start_task(task, self.cr_folder)

        if self.live:
            task = LiveRecordDownloader(download_script_repo=self.download_script_repo,
                                        repo=os.path.join(self.repo, self.lr_folder),
                                        up=self.up)
            self.start_task(task, self.lr_folder)

    def start_task(self, task, folder):
        if check_path(os.path.join(self.repo, folder)):
            task.logger.info(f'{folder} path check success')
            task.main()
        else:
            task.logger.info(f'{folder} path check fail')


class Downloader:
    logger = get_file_logger(logging.DEBUG, 'downloader')

    def __init__(self, download_script_repo, settings, upper_repo):
        self.download_script_repo = get_abs(download_script_repo)
        self.settings = get_abs(settings)
        self.upper_repo = get_abs(upper_repo)

    def main(self):
        self.logger.debug(f'pid:{os.getpid()}')
        if os.path.exists(self.settings):
            self.logger.info('有配置文件，开始运行')
            infos = self.info_parse(self.read(self.settings))
            for info in infos:
                self.logger.info(f'为uid:{info.get("uid")}的用户开始下载')
                task = Task(self.download_script_repo, self.upper_repo, info.get('uid'),
                            info.get('live'), info.get('custom'))
                task.main()
            self.logger.info('成功！ 等待下一次唤醒...')
        else:
            self.logger.info('无配置文件，初始化后退出。。。')
            self.init_setting()

    def info_parse(self, infos):
        return list(map(lambda info: {infos[0][i]: info[i] for i in range(len(info))}, infos[1:]))

    def read(self, file_path):
        file = xlrd.open_workbook(file_path)
        sheet = file.sheet_by_index(0)
        return [sheet.row_values(r) for r in range(sheet.nrows)]

    def init_setting(self):
        data = [['uid', 'live', 'custom']]
        self.save(self.settings, data)

    def save(self, file_path, data):
        file = xlwt.Workbook()
        sheet = file.add_sheet('BilibiliUP')
        for j in range(len(data)):
            for k in range(len(data[j])):
                sheet.write(j, k, data[j][k])
        file.save(file_path)
        self.logger.info('up info saved')
