# -*- coding: utf-8 -*-#

import logging
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
    def __init__(self, uid, start_script_repo_path, repo_path, logger: logging.Logger):
        self.uid = int(uid) if isinstance(uid, str) else uid
        self.download_script_repo_path = start_script_repo_path
        self.repo_path = repo_path
        self.logger = logger

    def main(self):
        bv = self.get_bvs()
        self.start_download(bv)

    @staticmethod
    def copy_(source_path, target_path):
        os.system('cp "{}" "{}"'.format(source_path, target_path))

    @staticmethod
    def del_(source_path):
        os.system('rm "{}"'.format(source_path))

    def get_bvs(self):
        bvids = []
        page = 1
        while True:
            vlist = user.get_videos_raw(uid=self.uid, pn=page).get('list').get('vlist')
            if len(vlist):
                bvids.extend([video.get('bvid') for video in vlist])
                page += 1
            else:
                break
        bvids = set(bvids)
        self.logger.info('got bvids,length:{}'.format(len(bvids)))
        return bvids

    def start_download(self, bvs):
        def clear_tem_download(download_repo, del_fun):
            for i in os.listdir(download_repo):
                del_fun(os.path.join(download_repo, i))

        def get_nonexistent_pages(repo_path, bv, logger):
            pages = len(V.get_pages(bv))
            exist_pages = {}
            for i in range(1, pages + 1):
                exist_pages[str(i)] = False
            for unit in os.listdir(repo_path):
                if os.path.isfile(os.path.join(repo_path, unit)) and re.search(bv, unit):
                    result = re.search(',P(\d),', unit)
                    if result:
                        exist_pages[result.group(1)] = True
            np = list(map(lambda x: int(x), filter(lambda x: not exist_pages.get(x), exist_pages.keys())))
            logger.info('got nonexistent_pages,length:{}'.format(np))
            return np

        def download(download_script_path, pages, bv):
            pages = list(map(lambda x: str(x), pages))
            python_ver_and_script = 'python3 {}'.format(download_script_path)  # python & download script path
            highest_image_quality = '--ym'
            continued_download = '--yac'
            delete_useless_file_after_downloading = '--yad'
            delete_by_product_caption_after_downloading = '--nbd'
            add_avbv2filename = '--in'
            use_aria2c = '--ar'
            aria2c_speed = '--ms 3M'
            overwrite_duplicate_files = '-y'
            download_video_method = '-d 3'  # 1.当前弹幕 2.全弹幕 3.视频 4.当前弹幕+视频 5.全弹幕+视频 6.仅字幕 7.仅封面图片 8.仅音频
            download_audio_method = '-d 8'
            page = '-p {}'.format(','.join(pages))
            input_ = '-i {}'.format(bv)
            download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                         delete_useless_file_after_downloading,
                                         delete_by_product_caption_after_downloading, add_avbv2filename, use_aria2c,
                                         aria2c_speed, overwrite_duplicate_files, download_video_method, page, input_]
            download_audio_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                         delete_useless_file_after_downloading,
                                         delete_by_product_caption_after_downloading, add_avbv2filename, use_aria2c,
                                         aria2c_speed, overwrite_duplicate_files, download_audio_method, page, input_]
            os.system(' '.join(download_video_parameters))
            os.system(' '.join(download_audio_parameters))

        # clear_tem_download(os.path.join(self.download_script_repo_path, 'Download'), self.del_)
        os.chdir(self.download_script_repo_path)
        for bv in tqdm(bvs):
            nonexistent_pages = get_nonexistent_pages(self.repo_path, bv, self.logger)
            if len(nonexistent_pages):
                download(os.path.join(self.download_script_repo_path, 'start.py'), nonexistent_pages, bv)
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
    logger = logging.getLogger('CR')
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    CRDownloader = CustomRecordDownloader(9035182, r'E:\playground\from github\bili',
                                          r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_custom', logger)
    CRDownloader.main()


if __name__ == '__main__':
    main()
