# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: download.py
# @time: 2/20/2021 1:00 PM
import logging
import os
import json
from BilibiliManager.public import get_logger
from BilibiliManager.UP import UPTask


class Downloader:
    logger = get_logger('main', logging.DEBUG, False, True)

    def __init__(self, download_script_repo, settings, upper_repo):
        self.download_script_repo = os.path.abspath(download_script_repo)
        self.setting_path = os.path.abspath(settings)
        self.upper_repo = os.path.abspath(upper_repo)

    def main(self):
        def is_normal():
            return reload < MAX_RELOAD

        reload = 0
        MAX_RELOAD = 3
        while is_normal():
            try:
                self.logger.debug(f'pid:{os.getpid()}')
                if self.has_settings():
                    self.logger.info('有配置文件，开始运行')
                    for up in self.read(self.setting_path):
                        uid = up.get('uid')
                        if uid == '0':
                            continue
                        live = up.get('live')
                        custom = up.get('custom')
                        UPTask(self.download_script_repo, self.logger, self.upper_repo, uid, live, custom).main()
                    self.logger.info('成功！ 等待下一次唤醒...')
                else:
                    self.logger.info('无配置文件，初始化后退出。。。')
                    self.init_setting()
                break
            except Exception as e:
                print(e)
                reload += 1
        if is_normal():
            return True
        else:
            return False

    def has_settings(self):
        return os.path.exists(self.setting_path)

    @staticmethod
    def read(path):
        with open(path, encoding='utf-8') as file:
            info = json.loads(file.read())
        return info

    def init_setting(self):
        self.save(self.setting_path, [{'name': '此处填名字', 'uid': '0', 'live': False, 'custom': True}])

    @staticmethod
    def save(path, data):
        with open(path, 'w', encoding='utf-8') as file:
            # ensure_ascii=False, encoding='utf-8'
            content = json.dumps(data,ensure_ascii=False)
            file.write(content)
        # @staticmethod
        # def get_info(file_path):
        #     file = xlrd.open_workbook(file_path)
        #     sheet = file.sheet_by_index(0)
        #     raw_info = [sheet.row_values(r) for r in range(sheet.nrows)]
        #     info = [{raw_info[0][i]: r[i] for i in range(len(r))} for r in raw_info[1:]]
        #     return info

        # def init_setting(self):
        #     self.save([['uid', 'live', 'custom']])
        #
        # def save(self, data):
        #     file = xlwt.Workbook()
        #     sheet = file.add_sheet('BilibiliUP')
        #     for j in range(len(data)):
        #         for k in range(len(data[j])):
        #             sheet.write(j, k, data[j][k])
        #     file.save(self.setting_path)
        #     self.logger.info('up info saved')
