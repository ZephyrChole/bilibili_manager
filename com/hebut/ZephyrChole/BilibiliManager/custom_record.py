# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: custom_record.py
# @time: 2/20/2021 12:58 PM
import os
import logging
from subprocess import Popen, TimeoutExpired
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
        self.logger.info(f'{self.up.name} uid:{self.up.uid} start to inspect custom records')
        bv = self.get_infos()
        self.start_download(iter(bv))

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
        try:
            bv = next(bvs)
            self.download_loop(bv, [i for i in range(len(V.get_pages(bv)))])
            self.start_download(bvs)
        except StopIteration:
            pass

    def download_loop(self, bv, pages, attempt=0):
        self.logger.info(f'new download started:{bv}')
        try:
            self.download(bv, pages)
        except TimeoutExpired:
            if attempt > 3:
                self.logger.info(f'{bv} download timeout,skipping...')
            else:
                self.logger.info(f'{bv} download timeout,{attempt} attempt')
                self.download_loop(bv, pages, attempt + 1)

    def download(self, bv, pages):
        cwd = os.getcwd()
        os.chdir(self.download_script_repo)
        pages = list(map(lambda x: str(x), pages))
        # python & download script path
        python_ver_and_script = ('python3', os.path.join(self.download_script_repo, "start.py"))
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
        silent_mode = ('-s',)
        download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading,
                                     delete_by_product_caption_after_downloading, add_avbv2filename,
                                     redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                     not_overwrite_duplicate_files, download_video_method, page, input_, target_dir,
                                     not_show_in_explorer, silent_mode]
        download_audio_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading,
                                     delete_by_product_caption_after_downloading, add_avbv2filename,
                                     redownload_after_download, use_ffmpeg, use_aria2c, aria2c_speed,
                                     not_overwrite_duplicate_files, download_audio_method, page, input_, target_dir,
                                     not_show_in_explorer, silent_mode]
        parameters = []
        for p in download_video_parameters:
            parameters.extend(p)
        Popen(parameters, stdout=open(os.devnull, 'w')).wait(60 * 60)
        parameters = []
        for p in download_audio_parameters:
            parameters.extend(p)
        Popen(parameters, stdout=open(os.devnull, 'w')).wait(60 * 60)
        os.chdir(cwd)
