# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: live_record.py
# @time: 2/20/2021 12:44 PM

import logging
import os
import re
from subprocess import Popen, TimeoutExpired, DEVNULL
from com.hebut.ZephyrChole.BilibiliManager.public import RecordDownloader, check_path, get_file_logger, \
    get_headless_browser


class LiveRecordDownloadInfo:
    def __init__(self, url, date_str):
        self.url = url
        self.id = re.search('([^/]+)$', url).group(1)
        self.init_date(date_str)

    def init_date(self, date_str):
        result = re.match('(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2})', date_str)
        self.yyyy = result.group(1)
        self.mm = result.group(2)
        self.dd = result.group(3)
        self.HH = result.group(4)
        self.MM = result.group(5)

    def get_date(self):
        return '{}{}{}'.format(self.yyyy, self.mm, self.dd)


class LiveRecordDownloader(RecordDownloader):
    def __init__(self, download_script_repo, repo, up):
        self.download_script_repo = download_script_repo
        self.repo = repo
        self.up = up
        self.logger = get_file_logger(logging.DEBUG, f'lr up:{self.up.uid}-{self.up.name}')

    def main(self):
        self.logger.info(self.up.name)
        self.logger.info('live_url:{} start to inspect live records'.format(self.up.live_url))
        download_infos = self.get_infos()
        self.start_download(iter(download_infos))

    def get_infos(self):
        def enter_live():
            self.logger.info('entered live')
            browser.get(self.up.live_url)
            browser.implicitly_wait(60)

        def get_record_page():
            try:
                browser.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative').click()
                self.logger.info('got record page')
                return True
            except:
                self.logger.warning("can't find record button")
                return False

        def get_url_and_date():
            url = browser.find_element_by_css_selector(
                'div.live-record-card-cntr.card:nth-child({}) a'.format(count)).get_attribute('href')
            date = browser.find_element_by_css_selector(
                'div.live-record-card-cntr.card:nth-child({}) a p:last-child'.format(count)).text
            return url, date

        def forward_page():
            try:
                browser.find_element_by_css_selector('li.panigation.ts-dot-4.selected+li').click()
                browser.implicitly_wait(60)
                self.logger.debug('page forward')
                return True
            except:
                return False

        browser = get_headless_browser()
        enter_live()
        a = 0
        while a < 3:
            a += 1
            if get_record_page():
                break
            else:
                enter_live()
        download_infos = []
        while True:
            count = 1
            while True:
                try:
                    url, date = get_url_and_date()
                    download_infos.append(LiveRecordDownloadInfo(url, date))
                    count += 1
                except:
                    break
            if not forward_page():
                break
        self.logger.info('got download_infos,length:{}'.format(len(download_infos)))
        browser.quit()
        return download_infos

    def start_download(self, infos):
        try:
            info = next(infos)
            repo_with_date = os.path.join(self.repo, info.get_date())
            self.download_loop(info.url, repo_with_date)
            self.start_download(infos)
        except StopIteration:
            pass

    def download_loop(self, url, repo_with_date, attempt=0):
        try:
            if check_path(repo_with_date):
                self.download(self.download_script_repo, url, repo_with_date)
                return True
            else:
                return False
        except TimeoutExpired:
            if attempt <= 3:
                self.logger.info('download timeout,{} attempt'.format(attempt))
                return self.download_loop(url, repo_with_date, attempt + 1)
            else:
                self.logger.info('download timeout,skipping...')
                return False

    def download(self, download_script_repo, url, tar_dir):
        cwd = os.getcwd()
        os.chdir(download_script_repo)
        # python & download script path
        python_ver_and_script = ('python3', os.path.join(download_script_repo, "start.py"))
        highest_image_quality = ('--ym',)
        continued_download = ('--yac',)
        delete_useless_file_after_downloading = ('--yad',)
        not_delete_by_product_caption_after_downloading = ('--bd',)
        add_avbv2filename = ('--in',)
        redownload_after_download = ('--yr',)
        use_ffmpeg = ('--yf',)
        use_aria2c = ('--ar',)
        aria2c_speed = ('--ms', '3m')
        not_overwrite_duplicate_files = ('-n',)
        download_video_method = ('-d', '1')  # 1.视频 2.弹幕 3.视频+弹幕
        input_ = ('-i', url)
        target_dir = ('-o', tar_dir)
        not_show_in_explorer = ('--nol',)  # only valid on windows system.
        download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading, redownload_after_download, use_ffmpeg,
                                     not_delete_by_product_caption_after_downloading, add_avbv2filename, use_aria2c,
                                     aria2c_speed, not_overwrite_duplicate_files, download_video_method, input_,
                                     target_dir, not_show_in_explorer]
        parameters = []
        for p in download_video_parameters:
            parameters.extend(p)
        Popen(parameters, stdout=DEVNULL).wait(60 * 60)
        os.chdir(cwd)
