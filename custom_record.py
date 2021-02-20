# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: custom_record.py
# @time: 2/20/2021 12:58 PM
import os
import re

from bilibili_api import user
from bilibili_api import video as V
from tqdm import tqdm


class CustomRecordDownloader:
    def __init__(self, uid, start_script_repo_path, repo_path):
        self.uid = int(uid) if isinstance(uid, str) else uid
        self.download_script_repo_path = start_script_repo_path
        self.repo_path = repo_path

    def main(self):
        bv = self.get_bvs()
        self.download(bv)

    @staticmethod
    def copy_(source_path, target_path):
        os.system('cp "{}" "{}"'.format(source_path, target_path))

    @staticmethod
    def del_(source_path):
        os.system('rm "{}"'.format(source_path))

    def get_bvs(self):
        return [video.get('bvid') for video in user.get_videos_raw(uid=self.uid).get('list').get('vlist')]

    def download(self, bvs):
        def clear_tem_download(download_repo, del_fun):
            for i in os.listdir(download_repo):
                del_fun(os.path.join(download_repo, i))

        def check_for_exists(repo_path, bv):
            pages = len(V.get_pages(bv))
            exists = list(filter(lambda x: os.path.isfile(os.path.join(repo_path, x)) and re.search(bv, x),
                                 os.listdir(repo_path)))
            return pages == len(exists)

        clear_tem_download(os.path.join(self.download_script_repo_path, 'Download'), self.del_)
        os.chdir(self.download_script_repo_path)
        for bv in tqdm(bvs):
            if not check_for_exists(self.repo_path, bv):
                os.system('python3 "{}" --ym --yac --yad --yf --ar --yda --nbd --nol --in -y -d 3 -p a -i {}'.format(
                    os.path.join(self.download_script_repo_path, 'start.py'), bv))
                self.organize(bv)

    def organize(self, bv):
        def get_filename(keyword, download_script_repo_path):
            return list(filter(lambda x: re.search(keyword, x),
                               os.listdir(os.path.join(download_script_repo_path, 'Download'))))

        file_names = get_filename(bv, self.download_script_repo_path)
        for file_name in file_names:
            file_name = file_name
            if not os.path.exists(os.path.join(self.repo_path, file_name)):
                self.copy_(os.path.join(self.download_script_repo_path, 'Download', file_name),
                           os.path.join(self.repo_path, file_name))
            self.del_(os.path.join(self.download_script_repo_path, 'Download', file_name))


def main():
    c = CustomRecordDownloader(9035182, r'E:\playground\from github\bili',
                               r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_custom')
    c.main()


if __name__ == '__main__':
    main()
