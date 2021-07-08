# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: post_video.py
# @time: 2/20/2021 12:58 PM
import os
import re
from bilibili_api import user
from bilibili_api.video import get_pages
from BilibiliManager.public import RecordDownloader


class CustomInfo:
    def __init__(self, bv):
        self.id = bv
        self.pages = get_pages(bv)


class PostVideoDownloader(RecordDownloader):
    folder = 'custom_record'

    def get_info(self):
        infos = []
        page = 1
        while True:
            vlist = user.get_videos_raw(uid=self.up.uid, pn=page).get('list').get('vlist')
            if len(vlist):
                infos.extend([video.get('bvid') for video in vlist])
                page += 1
            else:
                break
        infos = list(map(lambda x: CustomInfo(x), set(infos)))
        self.logger.info('got infos,length:{}'.format(len(infos)))
        return infos

    def monitor_download(self, info):
        if self.is_complete(info, self.repo):
            self.logger.info(f'{info.id} exists')
            return True
        else:
            self.logger.info(f'new post video:{info.id}')
            a = self.download(info)
            if a:
                self.logger.info(f'{info.id} download success')
            else:
                pass
            return a

    def is_complete(self, info, tar_dir):
        count = 0
        for file in os.listdir(tar_dir):
            if re.search(info.id, file):
                count += 1
        return count == 2 * len(info.pages)

    def download(self, info):
        cwd = os.getcwd()
        os.chdir(self.download_script_repo)
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
        page = ('-p', 'a')
        input_ = ('-i', info.id)
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
        a = self.start_popen(parameters, cwd, 60 * 60)
        parameters = []
        for p in download_audio_parameters:
            parameters.extend(p)
        b = self.start_popen(parameters, cwd, 60 * 60)
        os.chdir(cwd)
        return a and b
