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
        sheet = file.add_sheet('Sheet1')
        for j in range(len(data)):
            for k in range(len(data[j])):
                sheet.write(j, k, data[j][k])
        file.save(file_path)

    @staticmethod
    def read(file_path):
        file = xlrd.open_workbook(file_path)
        data = []
        for sheet_count in range(len(file.sheets())):
            sheet = file.sheet_by_index(sheet_count)
            sheet_info = [sheet.row_values(i) for i in range(sheet.nrows)]
            data.append(sheet_info)
        return data

    def init_settings(self):
        data = [['uid', 'live', 'custom']]
        self.save(self.settings_filepath, data)

    def read_in(self):
        return self.read(self.settings_filepath)[0]

    @staticmethod
    def info_parse(infos):
        new_infos = []
        for info in infos[1:]:
            new_info = {}
            for i in range(len(info)):
                new_info[infos[0][i]] = info[i]
            new_infos.append(new_info)
        return new_infos

    def main(self):
        os.chdir('/home/pi/programs/bilibili_manager')
        download_script_repo_path = r'/media/pi/sda1/media/programs/bili'
        if os.path.exists(self.settings_filepath):
            infos = self.info_parse(self.read_in())
            for info in infos:
                bm = BilibiliManager(download_script_repo_path, info.get('uid'),
                                     r'/media/pi/sda1/media/bilibili_record', info.get('live'), info.get('custom'))
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
