# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2/19/2021 12:01 PM
import bilibili_api
import time
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import re
from bilibili_api import user

from typing import List


class RecordDownloadInfo:
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


class RecordDownloader:
    def __init__(self, live_id, start_script_repo_path, repo_path):
        self.live_id = live_id
        self.start_script_repo_path = start_script_repo_path
        self.repo_path = repo_path
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        # self.browser = webdriver.Chrome('./chromedriver.exe')
        self.browser.minimize_window()

    def main(self):
        self.enter_live()
        download_infos = self.get_urls()
        self.browser.quit()
        cwd = os.getcwd()
        self.download(download_infos)
        os.chdir(cwd)

    def enter_live(self):
        self.browser.get('https://live.bilibili.com/{}'.format(self.live_id))
        # time.sleep(10)
        WebDriverWait(self.browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative'))
        record_button = self.browser.find_element_by_css_selector('li.item:last-child>span.dp-i-block.p-relative')
        record_button.click()

    def get_urls(self):
        WebDriverWait(self.browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('div.right-container'))
        download_infos = []
        count = 1
        while True:
            try:
                url = self.browser.find_element_by_css_selector(
                    'div.live-record-card-cntr.card:nth-child({}) a'.format(count)).get_attribute('href')
                date = self.browser.find_element_by_css_selector(
                    'div.live-record-card-cntr.card:nth-child({}) a p:last-child'.format(count)).text
                download_infos.append(RecordDownloadInfo(url, date))
                count += 1
            except:
                break
        return download_infos

    def download(self, infos: List[RecordDownloadInfo]):
        def get_filename(repo_path, keyword):
            for i in os.listdir(repo_path):
                if os.path.isfile(os.path.join(repo_path, i)) and re.search(keyword, i):
                    return i

        def organize(download_path, info, repo_path):
            file_name = get_filename(download_path, re.search('([^/]+)$', info.url).group(1))
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path):
                os.mkdir(repo_folder_path)
            os.system(
                'copy "{}" "{}"'.format(os.path.join(download_path, file_name),
                                        os.path.join(repo_folder_path, file_name)))
            os.system('rm "{}"'.format(os.path.join(download_path, file_name)))

        def check_for_exists(info, repo_path):
            repo_folder_path = os.path.join(repo_path, info.get_date())
            if not os.path.exists(repo_folder_path) or not os.path.isdir(repo_folder_path):
                return False
            else:
                for file in os.listdir(repo_folder_path):
                    if re.search(info.id, file):
                        return True
            return False

        os.chdir(self.start_script_repo_path)
        for info in tqdm(infos):
            command = r'python "{}" --bd --ym --yac --yad --yr --yf -d 1 -p a -y -i {}'.format(
                os.path.join(self.start_script_repo_path, 'start.py'), info.url)
            if not check_for_exists(info, self.repo_path):
                os.system(command)
                organize(os.path.join(self.start_script_repo_path, 'Download'), info, self.repo_path)


class CustomVideoDownloader:
    def __init__(self, uid, start_script_repo_path, repo_path):
        self.uid = int(uid) if isinstance(uid, str) else uid
        self.download_script_repo_path = start_script_repo_path
        self.repo_path = repo_path

    def main(self):
        bv = self.get_bvs()
        self.download(bv)

    def get_bvs(self):
        bvs = []
        for video in user.get_videos_raw(uid=self.uid).get('list').get('vlist'):
            bvs.append(video.get('bvid'))
        return bvs

    def download(self, bvs):
        def check_for_exists(repo_path, bv):
            for i in os.listdir(repo_path):
                ipath = os.path.join(repo_path, i)
                if os.path.isfile(ipath) and re.search(bv, i):
                    return True
            return False

        os.chdir(self.download_script_repo_path)
        for bv in bvs:
            if not check_for_exists(self.repo_path, bv):
                os.system('python "{}" --ym --yac --yad --yf --ar --yda --nbd --in -y -d 3 -p a -i {}'.format(
                    os.path.join(self.download_script_repo_path, 'start.py'), bv))
                self.organize(bv)

    def organize(self, bv):
        def get_filename(keyword, download_script_repo_path):
            return list(filter(lambda x: re.search(keyword, x),
                               os.listdir(os.path.join(download_script_repo_path, 'Download'))))

        file_names = get_filename(bv, self.download_script_repo_path)
        for file_name in file_names:
            file_name = file_name
            os.system('copy "{}" "{}"'.format(os.path.join(self.download_script_repo_path, 'Download', file_name),
                                              os.path.join(self.repo_path, file_name)))
            os.system('del "{}"'.format(os.path.join(self.download_script_repo_path, 'Download', file_name)))


def record_video():
    r = RecordDownloader('3509872', r'E:\playground\from github\bili',
                         r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_record')
    r.main()


def custom_video():
    c = CustomVideoDownloader(9035182, r'E:\playground\from github\bili',
                              r'I:\media\bilibili_record\3509872-有毒的小蘑菇酱\test_custom')
    c.main()


def main():
    custom_video()
    record_video()


if __name__ == '__main__':
    main()
