# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: live_record.py
# @time: 2/20/2021 12:44 PM

import logging
import os
import re

import timeout_decorator
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


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


class LiveRecordDownloader:
    def __init__(self, live_id, download_script_repo_path, repo_path, logger: logging.Logger):
        self.live_id = live_id
        self.start_script_repo_path = download_script_repo_path
        self.repo_path = repo_path
        self.logger = logger
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.minimize_window()

    def main(self):
        self.logger.info('live_id:{} start to inspect live records'.format(self.live_id))
        try:
            self.enter_live()
            self.get_record_page()
            download_infos = self.get_urls()
            self.browser.quit()
            self.start_download(download_infos)
        except TimeoutException:
            self.logger.info("didn't find record page")
        except WebDriverException:
            self.logger.info('No internet,skipping...')

    @staticmethod
    def copy_(source_path, target_path):
        os.system('cp "{}" "{}"'.format(source_path, target_path))

    @staticmethod
    def del_(source_path):
        os.system('rm "{}"'.format(source_path))

    def enter_live(self):
        self.logger.info('entered live')
        self.browser.get('https://live.bilibili.com/{}'.format(self.live_id))

    def get_record_page(self):
        WebDriverWait(self.browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative'))
        record_button = self.browser.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative')
        record_button.click()
        self.logger.info('got record page')

    def get_urls(self):
        def get_url_and_date(browser, count):
            url = browser.find_element_by_css_selector(
                'div.live-record-card-cntr.card:nth-child({}) a'.format(count)).get_attribute('href')
            date = browser.find_element_by_css_selector(
                'div.live-record-card-cntr.card:nth-child({}) a p:last-child'.format(count)).text
            return url, date

        WebDriverWait(self.browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('div.right-container'))
        download_infos = []
        count = 1
        while True:
            try:
                url, date = get_url_and_date(self.browser, count)
                download_infos.append(LiveRecordDownloadInfo(url, date))
                count += 1
            except:
                break
        self.logger.info('got download_infos,length:{}'.format(len(download_infos)))
        return download_infos

    def start_download(self, infos):
        def clear_tem_download(download_repo, del_fun, logger):
            for i in os.listdir(download_repo):
                del_fun(os.path.join(download_repo, i))
            logger.info('cleared tem download')

        def get_filename(repo_path, keyword):
            for i in os.listdir(repo_path):
                if os.path.isfile(os.path.join(repo_path, i)) and re.search(keyword, i):
                    return i

        def organize(download_path, info, repo_path):
            file_name = get_filename(download_path, re.search('([^/]+)$', info.url).group(1))
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path):
                os.mkdir(repo_folder_path)
            self.copy_(os.path.join(download_path, file_name), os.path.join(repo_folder_path, file_name))
            self.del_(os.path.join(download_path, file_name))

        def check_for_exists(info, repo_path, logger):
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path) or not os.path.isdir(repo_folder_path):
                return False
            else:
                for file in os.listdir(repo_folder_path):
                    if re.search(info.id, file):
                        logger.info('{} exists'.format(info.id))
                        return True
            logger.info('{} not exist'.format(info.id))
            return False

        @timeout_decorator.timeout(60 * 60)
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

        # clear_tem_download(os.path.join(self.start_script_repo_path, 'Download'), self.del_, self.logger)
        cwd = os.getcwd()
        os.chdir(self.start_script_repo_path)
        for info in tqdm(infos):
            if not check_for_exists(info, self.repo_path, self.logger):
                attempt = 0
                while attempt <= 3:
                    try:
                        download(os.path.join(self.start_script_repo_path, 'start.py'), info.url)
                        organize(os.path.join(self.start_script_repo_path, 'Download'), info, self.repo_path)
                        break
                    except timeout_decorator.timeout_decorator.TimeoutError:
                        attempt += 1
                        self.logger.info('download timeout,{} attempt'.format(attempt))
                if attempt > 3:
                    self.logger.info('download timeout,skipping...')
        os.chdir(cwd)


def main():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    lrLogger = logging.getLogger('LR')
    lrLogger.setLevel(logging.INFO)
    lrLogger.addHandler(ch)
    lrDownloader = LiveRecordDownloader(live_id=3509872,
                                        download_script_repo_path=r'/media/pi/sda1/media/programs/bili',
                                        repo_path=os.path.join(
                                            r'/media/pi/sda1/media/bilibili_record/3509872-有毒的小蘑菇酱-official',
                                            'live_record'), logger=lrLogger)
    lrDownloader.main()


if __name__ == '__main__':
    main()
