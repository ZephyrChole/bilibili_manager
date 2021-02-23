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

    def __init__(self, uid, live_id, download_script_repo_path, repo_path, comment, live, custom):
        self.repo_path = repo_path
        self.download_script_repo_path = download_script_repo_path
        self.live = live
        self.custom = custom

        level = logging.DEBUG
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        self.crLogger = logging.getLogger('CR')
        self.crLogger.setLevel(level)
        self.crLogger.addHandler(ch)

        self.lrLogger = logging.getLogger('LR')
        self.lrLogger.setLevel(level)
        self.lrLogger.addHandler(ch)

        self.crDownloader = CustomRecordDownloader(uid=uid, download_script_repo_path=download_script_repo_path,
                                                   repo_path=os.path.join(repo_path, self.cr_folder),
                                                   logger=self.crLogger, comment=comment)
        self.lrDownloader = LiveRecordDownloader(live_id=live_id, download_script_repo_path=download_script_repo_path,
                                                 repo_path=os.path.join(repo_path, self.lr_folder),
                                                 logger=self.lrLogger, comment=comment)

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
            self.lrDownloader.main()
        if self.custom:
            self.crDownloader.main()


def main():
    os.chdir('/home/pi/programs/bilibili_manager')
    download_script_repo_path = r'/media/pi/sda1/media/programs/bili'
    XKXM = BilibiliManager(uid=14387072, live_id=6374209, download_script_repo_path=download_script_repo_path,
                           repo_path=r'/media/pi/sda1/media/bilibili_record/14387072-小可学妹-official', live=True,
                           custom=False, comment='小可学妹')
    XKXM.main()
    YDDXMGJ = BilibiliManager(uid=9035182, live_id=3509872, download_script_repo_path=download_script_repo_path,
                              repo_path=r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official', live=True,
                              custom=True, comment='有毒的小蘑菇酱')
    YDDXMGJ.main()
    YYXST = BilibiliManager(uid=358629230, live_id=13328782, download_script_repo_path=download_script_repo_path,
                            repo_path=r'/media/pi/sda1/media/bilibili_record/13328782-圆圆小石头-official', live=False,
                            custom=True, comment='圆圆小石头')
    YYXST.main()
    print('成功！ 等待下一次唤醒...')
    YDDXMGJ.clear_tem_download()


if __name__ == '__main__':
    main()
