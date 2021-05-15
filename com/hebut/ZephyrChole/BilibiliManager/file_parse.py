# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: file_parse.py
# @time: 3/1/2021 6:38 PM
import os
import xlrd
import xlwt
from com.hebut.ZephyrChole.BilibiliManager.public import get_abs
from com.hebut.ZephyrChole.BilibiliManager.download import Downloader


class FileParser:
    def __init__(self, download_script_repo, settings, upper_repo):
        self.download_script_repo = get_abs(download_script_repo)
        self.settings = get_abs(settings)
        self.upper_repo = get_abs(upper_repo)

    @staticmethod
    def save(file_path, data):
        file = xlwt.Workbook()
        sheet = file.add_sheet('BilibiliUP')
        for j in range(len(data)):
            for k in range(len(data[j])):
                sheet.write(j, k, data[j][k])
        file.save(file_path)

    @staticmethod
    def read(file_path):
        file = xlrd.open_workbook(file_path)
        sheet = file.sheet_by_index(0)
        return [sheet.row_values(r) for r in range(sheet.nrows)]

    def init_settings(self):
        data = [['uid', 'live', 'custom']]
        self.save(self.settings, data)

    @staticmethod
    def info_parse(infos):
        return list(map(lambda info: {infos[0][i]: info[i] for i in range(len(info))}, infos[1:]))

    def main(self):
        if os.path.exists(self.settings):
            infos = self.info_parse(self.read(self.settings))
            for info in infos:
                downloader = Downloader(self.download_script_repo, self.upper_repo, info.get('uid'),
                                        info.get('live'), info.get('custom'))
                downloader.main()
            print('成功！ 等待下一次唤醒...')
        else:
            self.init_settings()
