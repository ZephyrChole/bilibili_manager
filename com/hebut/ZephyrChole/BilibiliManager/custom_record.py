# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: custom_record.py
# @time: 2/20/2021 12:58 PM
import os
import re
import logging
from subprocess import Popen
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from bilibili_api import user
from bilibili_api import video as V
from com.hebut.ZephyrChole.BilibiliManager.public import RecordDownloader, get_file_logger


class CustomRecordDownloader(RecordDownloader):
    def __init__(self, download_script_repo, repo, up):
        self.download_script_repo = download_script_repo
        self.repo = repo
        self.up = up
        self.logger = get_file_logger(logging.DEBUG, f'cr up:{self.up.uid}-{self.up.name}')

    def main(self):
        self.logger.info(self.up.name)
        self.logger.info('uid:{} start to inspect custom records'.format(self.up.uid))
        bv = self.get_infos()
        self.start_download(bv)

    def get_infos(self, bvids=None, page=1):
        if bvids is None:
            bvids = []
        vlist = user.get_videos_raw(uid=self.up.uid, pn=page).get('list').get('vlist')
        if len(vlist):
            bvids.extend([video.get('bvid') for video in vlist])
            page += 1
            return self.get_infos(bvids, page + 1)
        else:
            self.logger.info('got bvids,length:{}'.format(len(bvids)))
            return set(bvids)

    def start_download(self, bvs):
        self.start_loop(iter(bvs))

    def start_loop(self, bvs):
        try:
            bv = next(bvs)
            nonexistent_pages = self.get_nonexistent_pages(self.repo, bv, self.logger)
            if len(nonexistent_pages):
                self.download_loop(bv, nonexistent_pages)
            self.start_loop(bvs)
        except StopIteration:
            pass

    def get_nonexistent_pages(self, repo, bv, logger):
        pages = len(V.get_pages(bv))
        exist_pages = {}
        for i in range(1, pages + 1):
            exist_pages[str(i)] = 0
        for unit in os.listdir(repo):
            if os.path.isfile(os.path.join(repo, unit)) and re.search(bv, unit):
                result = re.search(',P(\d+),', unit)
                if result and isinstance(exist_pages.get(result.group(1)), int):
                    exist_pages[result.group(1)] += 1
        np = list(map(lambda x: int(x), filter(lambda x: exist_pages.get(x) < 2, exist_pages.keys())))
        if len(np):
            logger.info('{} got nonexistent_pages,length:{}'.format(bv, np))
        return np

    def download_loop(self, bv, nonexistent_pages, attempt=0):
        try:
            self.download(bv, nonexistent_pages)
        except FunctionTimedOut:
            if attempt > 3:
                self.logger.info('download timeout,skipping...')
            else:
                self.logger.info('download timeout,{} attempt'.format(attempt))
                self.download_loop(bv, nonexistent_pages, attempt + 1)

    @func_set_timeout(60 * 60)
    def download(self, bv, nonexistent_pages):
        cwd = os.getcwd()
        os.chdir(self.download_script_repo)
        pages = list(map(lambda x: str(x), nonexistent_pages))
        python_ver_and_script = (
            'python3', os.path.join(self.download_script_repo, "start.py"))  # python & download script path
        highest_image_quality = ('--ym',)
        continued_download = ('--yac',)
        delete_useless_file_after_downloading = ('--yad',)
        delete_by_product_caption_after_downloading = ('--nbd',)
        add_avbv2filename = ('--in',)
        redownload_after_download = ('--yr',)
        use_ffmpeg = ('--yf',)
        use_aria2c = ('--ar',)
        aria2c_speed = ('--ms', '3m',)
        not_overwrite_duplicate_files = ('-n',)
        download_video_method = ('-d', '3')  # 1.当前弹幕 2.全弹幕 3.视频 4.当前弹幕+视频 5.全弹幕+视频 6.仅字幕 7.仅封面图片 8.仅音频
        download_audio_method = ('-d', '8')
        page = ('-p', ",".join(pages))
        input_ = ('-i', bv)
        target_dir = ('-o', self.repo)
        not_show_in_explorer = ('--nol',)  # only valid on windows system.
        download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading,
                                     delete_by_product_caption_after_downloading, add_avbv2filename,
                                     redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                     not_overwrite_duplicate_files, download_video_method, page, input_, target_dir,
                                     not_show_in_explorer]
        download_audio_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading,
                                     delete_by_product_caption_after_downloading, add_avbv2filename,
                                     redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                     not_overwrite_duplicate_files, download_audio_method, page, input_, target_dir,
                                     not_show_in_explorer]
        parameters = []
        for p in download_video_parameters:
            parameters.extend(p)
        Popen(parameters, stdout=open(os.devnull)).wait()
        parameters = []
        for p in download_audio_parameters:
            parameters.extend(p)
        Popen(parameters, stdout=open(os.devnull)).wait()
        os.chdir(cwd)
