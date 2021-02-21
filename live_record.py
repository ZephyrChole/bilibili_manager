# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: live_record.py
# @time: 2/20/2021 12:44 PM

import os
import re

from selenium import webdriver
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
    def __init__(self, live_id, start_script_repo_path, repo_path):
        self.live_id = live_id
        self.start_script_repo_path = start_script_repo_path
        self.repo_path = repo_path
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.minimize_window()

    def main(self):
        self.enter_live()
        self.get_record_page()
        download_infos = self.get_urls()
        self.browser.quit()
        self.download(download_infos)

    @staticmethod
    def copy_(source_path, target_path):
        os.system('cp "{}" "{}"'.format(source_path, target_path))

    @staticmethod
    def del_(source_path):
        os.system('rm "{}"'.format(source_path))

    def enter_live(self):
        self.browser.get('https://live.bilibili.com/{}'.format(self.live_id))

    def get_record_page(self):
        WebDriverWait(self.browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative'))
        record_button = self.browser.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative')
        record_button.click()

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
        return download_infos

    def download(self, infos):
        def clear_tem_download(download_repo, del_fun):
            for i in os.listdir(download_repo):
                del_fun(os.path.join(download_repo, i))

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

        def check_for_exists(info, repo_path):
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path) or not os.path.isdir(repo_folder_path):
                return False
            else:
                for file in os.listdir(repo_folder_path):
                    if re.search(info.id, file):
                        return True
            return False

        clear_tem_download(os.path.join(self.start_script_repo_path, 'Download'), self.del_)
        cwd = os.getcwd()
        os.chdir(self.start_script_repo_path)
        for info in tqdm(infos):
            command = r'python3 "{}" --bd --ym --yac --yad --yr --nol --yf --ms 3M -d 1 -p a -y -i {}'.format(
                os.path.join(self.start_script_repo_path, 'start.py'), info.url)
            if not check_for_exists(info, self.repo_path):
                os.system(command)
                organize(os.path.join(self.start_script_repo_path, 'Download'), info, self.repo_path)
        os.chdir(cwd)


def main():
    r = LiveRecordDownloader('3509872', r'E:\playground\from github\bili',
                             r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_record')
    r.main()


if __name__ == '__main__':
    main()
