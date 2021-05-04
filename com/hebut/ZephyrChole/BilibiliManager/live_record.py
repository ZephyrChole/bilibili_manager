# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: live_record.py
# @time: 2/20/2021 12:44 PM

import logging
import os
import re
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

from com.hebut.ZephyrChole.BilibiliManager.public import RecordDownloader


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
    def __init__(self, download_script_repo_path, repo_path, logger: logging.Logger, up):
        self.download_script_repo_path = download_script_repo_path
        self.repo_path = repo_path
        self.logger = logger
        self.name = up.name
        self.live_url = up.live_url

    @staticmethod
    def get_browser():
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options)

    def main(self):
        self.logger.info(self.name)
        self.logger.info('live_url:{} start to inspect live records'.format(self.live_url))
        download_infos = self.get_infos()
        self.start_download(download_infos)

    def get_infos(self):
        def enter_live():
            self.logger.info('entered live')
            browser.get(self.live_url)
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

        browser = self.get_browser()
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
        def check_for_exists(info, repo_path, logger):
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path) or not os.path.isdir(repo_folder_path):
                return False
            else:
                for file in os.listdir(repo_folder_path):
                    if re.search(info.id, file):
                        logger.debug('{} exists'.format(info.id))
                        return True
            logger.debug('{} not exist'.format(info.id))
            return False

        @func_set_timeout(60 * 60)
        def download(download_script_path, url):
            python_ver_and_script = 'python3 {}'.format(download_script_path)  # python & download script path
            highest_image_quality = '--ym'
            continued_download = '--yac'
            delete_useless_file_after_downloading = '--yad'
            not_delete_by_product_caption_after_downloading = '--bd'
            add_avbv2filename = '--in'
            redownload_after_download = '--yr'
            use_ffmpeg = '--yf'
            use_aria2c = '--ar'
            aria2c_speed = '--ms 3m'
            not_overwrite_duplicate_files = '-n'
            download_video_method = '-d 1'  # 1.视频 2.弹幕 3.视频+弹幕
            input_ = '-i {}'.format(url)
            download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                         delete_useless_file_after_downloading, redownload_after_download, use_ffmpeg,
                                         not_delete_by_product_caption_after_downloading, add_avbv2filename, use_aria2c,
                                         aria2c_speed, not_overwrite_duplicate_files, download_video_method, input_]
            os.system(' '.join(download_video_parameters))

        def organize(info, start_script_repo_path, repo_path):
            def copy_(source_path, target_path):
                os.system('cp "{}" "{}"'.format(source_path, target_path))

            def del_(source_path):
                os.system('rm "{}"'.format(source_path))

            def get_filename(repo_path, keyword):
                for i in os.listdir(repo_path):
                    if os.path.isfile(os.path.join(repo_path, i)) and re.search(keyword, i):
                        return i

            download_path = os.path.join(start_script_repo_path, 'Download')
            file_name = get_filename(download_path, re.search('([^/]+)$', info.url).group(1))
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path):
                os.mkdir(repo_folder_path)
            copy_(os.path.join(download_path, file_name), os.path.join(repo_folder_path, file_name))
            del_(os.path.join(download_path, file_name))

        for info in tqdm(infos):
            if not check_for_exists(info, self.repo_path, self.logger):
                attempt = 0
                while attempt <= 3:
                    try:
                        download(os.path.join(self.download_script_repo_path, 'start.py'), info.url)
                        organize(info, self.download_script_repo_path, self.repo_path)
                        break
                    except FunctionTimedOut:
                        attempt += 1
                        self.logger.info('download timeout,{} attempt'.format(attempt))
                if attempt > 3:
                    self.logger.info('download timeout,skipping...')
