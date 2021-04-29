# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: file_parse.py
# @time: 3/1/2021 6:38 PM
import os

import xlrd
import xlwt

from bibibili_manager import BilibiliManager


class FileParser:
    def __init__(self, settings_filepath):
        self.settings_filepath = settings_filepath

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
        self.save(self.settings_filepath, data)

    @staticmethod
    def info_parse(infos):
        return list(map(lambda info: {infos[0][i]: info[i] for i in range(len(info))}, infos[1:]))

    def main(self):
        download_script_repo_path = '../bili'
        if os.path.exists(self.settings_filepath):
            infos = self.info_parse(self.read(self.settings_filepath))
            for info in infos:
                bm = BilibiliManager(download_script_repo_path, info.get('uid'), '../', info.get('live'),
                                     info.get('custom'))
                bm.main()
                bm.clear_tem_download()
            print('成功！ 等待下一次唤醒...')
        else:
            self.init_settings()


def main():
    fp = FileParser('settings.xls')
    fp.main()


if __name__ == '__main__':
    main()
