# -*- coding: utf-8 -*-#

import logging
# Author:Jiawei Feng
# @software: PyCharm
# @file: custom_record.py
# @time: 2/20/2021 12:58 PM
import os
import re

import timeout_decorator
from bilibili_api import user
from bilibili_api import video as V
from tqdm import tqdm

from record_download import RecordDownloader


class CustomRecordDownloader(RecordDownloader):
    def __init__(self, uid, download_script_repo_path, repo_path, logger: logging.Logger, name):
        self.uid = int(uid) if isinstance(uid, str) else uid
        self.download_script_repo_path = download_script_repo_path
        self.repo_path = repo_path
        self.logger = logger
        self.comment = name

    def main(self):
        self.logger.info(self.comment)
        self.logger.info('uid:{} start to inspect custom records'.format(self.uid))
        bv = self.get_infos()
        self.start_download(bv)

    def get_infos(self):
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
        def get_nonexistent_pages(repo_path, bv, logger):
            pages = len(V.get_pages(bv))
            exist_pages = {}
            for i in range(1, pages + 1):
                exist_pages[str(i)] = 0
            for unit in os.listdir(repo_path):
                if os.path.isfile(os.path.join(repo_path, unit)) and re.search(bv, unit):
                    result = re.search(',P(\d+),', unit)
                    if result and isinstance(exist_pages.get(result.group(1)), int):
                        exist_pages[result.group(1)] += 1
            np = list(map(lambda x: int(x), filter(lambda x: exist_pages.get(x) < 2, exist_pages.keys())))
            if len(np):
                logger.info('{} got nonexistent_pages,length:{}'.format(bv, np))
            return np

        @timeout_decorator.timeout(60 * 60)
        def download(download_script_path, pages, bv):
            pages = list(map(lambda x: str(x), pages))
            python_ver_and_script = 'python3 {}'.format(download_script_path)  # python & download script path
            highest_image_quality = '--ym'
            continued_download = '--yac'
            delete_useless_file_after_downloading = '--yad'
            delete_by_product_caption_after_downloading = '--nbd'
            add_avbv2filename = '--in'
            redownload_after_download = '--yr'
            use_ffmpeg = '--yf'
            use_aria2c = '--ar'
            aria2c_speed = '--ms 3m'
            not_overwrite_duplicate_files = '-n'
            download_video_method = '-d 3'  # 1.当前弹幕 2.全弹幕 3.视频 4.当前弹幕+视频 5.全弹幕+视频 6.仅字幕 7.仅封面图片 8.仅音频
            download_audio_method = '-d 8'
            page = '-p {}'.format(','.join(pages))
            input_ = '-i {}'.format(bv)
            download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                         delete_useless_file_after_downloading,
                                         delete_by_product_caption_after_downloading, add_avbv2filename,
                                         redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                         not_overwrite_duplicate_files, download_video_method, page, input_]
            download_audio_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                         delete_useless_file_after_downloading,
                                         delete_by_product_caption_after_downloading, add_avbv2filename,
                                         redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                         not_overwrite_duplicate_files, download_audio_method, page, input_]
            os.system(' '.join(download_video_parameters))
            os.system(' '.join(download_audio_parameters))

        def organize(bv, download_script_repo_path, repo_path):
            def copy_(source_path, target_path):
                os.system('cp "{}" "{}"'.format(source_path, target_path))

            def del_(source_path):
                os.system('rm "{}"'.format(source_path))

            def get_filename(keyword, download_script_repo_path):
                return list(filter(lambda x: re.search(keyword, x),
                                   os.listdir(os.path.join(download_script_repo_path, 'Download'))))

            file_names = get_filename(bv, download_script_repo_path)
            for file_name in file_names:
                file_name = file_name
                if not os.path.exists(os.path.join(repo_path, file_name)):
                    copy_(os.path.join(download_script_repo_path, 'Download', file_name),
                          os.path.join(repo_path, file_name))
                del_(os.path.join(download_script_repo_path, 'Download', file_name))

        # clear_tem_download(os.path.join(self.download_script_repo_path, 'Download'), self.del_)
        os.chdir(self.download_script_repo_path)
        for bv in tqdm(bvs):
            nonexistent_pages = get_nonexistent_pages(self.repo_path, bv, self.logger)
            if len(nonexistent_pages):
                attempt = 0
                while attempt <= 3:
                    try:
                        download(os.path.join(self.download_script_repo_path, 'start.py'), nonexistent_pages, bv)
                        organize(bv, self.download_script_repo_path, self.repo_path)
                        break
                    except timeout_decorator.timeout_decorator.TimeoutError:
                        attempt += 1
                        self.logger.info('download timeout,{} attempt'.format(attempt))
                if attempt > 3:
                    self.logger.info('download timeout,skipping...')


def main():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    crLogger = logging.getLogger('CR')
    crLogger.setLevel(logging.INFO)
    crLogger.addHandler(ch)
    crDownloader = CustomRecordDownloader(uid=9035182, download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                                          repo_path=os.path.join(
                                              r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official/',
                                              'custom_record'), logger=crLogger, name='有毒的小蘑菇酱')
    crDownloader.main()


if __name__ == '__main__':
    main()
