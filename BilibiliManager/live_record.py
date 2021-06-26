# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: live_record.py
# @time: 2/20/2021 12:44 PM
import os
import re
from BilibiliManager.public import RecordDownloader, check_path, get_headless_browser


class LiveInfo:
    def __init__(self, url, date_str):
        self.url = url
        self.id = re.search('([^/]+)$', url).group(1)
        result = re.match('(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2})', date_str)
        self.yyyy = result.group(1)
        self.mm = result.group(2)
        self.dd = result.group(3)
        self.HH = result.group(4)
        self.MM = result.group(5)

    def get_date(self):
        return '{}{}{}'.format(self.yyyy, self.mm, self.dd)


class LiveRecordDownloader(RecordDownloader):
    folder = 'live_record'

    def get_info(self):
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
                    download_infos.append(LiveInfo(url, date))
                    count += 1
                except:
                    break
            if not forward_page():
                break
        self.logger.info('got download_infos,length:{}'.format(len(download_infos)))
        browser.quit()
        return download_infos

    def monitor_download(self, info):
        repo_with_date = os.path.join(self.repo, info.get_date())
        if check_path(repo_with_date):
            if self.isExist(info, repo_with_date) and not self.has_tem(info.id, repo_with_date):
                self.logger.info(f'{info.id} exists')
                return True
            else:
                self.logger.info(f'new download started:{info.id}')
                a = self.download(info.url, repo_with_date)
                self.clear_tem(info.id, repo_with_date)
                return a
        else:
            self.logger.error('date folder check failed')
            return True

    def isExist(self, info, tar_dir):
        for file in os.listdir(tar_dir):
            if re.search(info.id, file):
                return True
        return False

    def has_tem(self, key_word, repo_with_date):
        for file in os.listdir(repo_with_date):
            if self.is_tem(key_word, file):
                return True
        return False

    @staticmethod
    def is_tem(key_word, file):
        unfinish_finder = re.compile('_\d+.flv')
        id_finder = re.compile(key_word)
        return unfinish_finder.search(file) and id_finder.search(file)

    def clear_tem(self, key_word, repo_with_date):
        for file in os.listdir(repo_with_date):
            if self.is_tem(key_word, file):
                full_path = os.path.join(repo_with_date, file)
                os.remove(full_path)
                self.logger.info(f'未完成下载:{full_path},已删除')

    def download(self, url, tar_dir):
        cwd = os.getcwd()
        os.chdir(self.download_script_repo)
        # python & download script path
        python_ver_and_script = ('python3', os.path.join(self.download_script_repo, "start.py"))
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
        silent_mode = ('-s',)
        download_video_parameters = [python_ver_and_script, highest_image_quality, continued_download,
                                     delete_useless_file_after_downloading, redownload_after_download, use_ffmpeg,
                                     not_delete_by_product_caption_after_downloading, add_avbv2filename, use_aria2c,
                                     aria2c_speed, not_overwrite_duplicate_files, download_video_method, input_,
                                     target_dir, not_show_in_explorer, silent_mode]
        parameters = []
        for p in download_video_parameters:
            parameters.extend(p)
        a = self.start_popen(parameters, cwd)
        os.chdir(cwd)
        return a