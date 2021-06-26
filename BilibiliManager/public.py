# -*- coding: utf-8 -*-#fv

# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2/22/2021 9:36 PM
import os
import time
import logging
from abc import ABCMeta, abstractmethod
from subprocess import Popen, TimeoutExpired
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def check_path(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        path = os.path.split(dir_path)[0]
        if check_path(path):
            try:
                os.mkdir(dir_path)
                return True
            except:
                return False
        else:
            return False


def get_file_logger(level, name):
    formatter = logging.Formatter("%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh = logging.FileHandler('./log/{}.log'.format(time.strftime("%Y-%m-%d", time.localtime())),
                             encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return logger


def get_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


class RecordDownloader(metaclass=ABCMeta):
    folder = 'default'
    max_retry = 3

    def __init__(self, download_script_repo, upper_repo, up):
        self.download_script_repo = download_script_repo
        self.repo = os.path.join(upper_repo, self.folder)
        self.up = up
        self.logger = get_file_logger(logging.DEBUG, f'downloader uid:{self.up.uid} folder:{self.folder}')

    def main(self):
        self.logger.info(f'{self.folder} download start')
        if check_path(self.repo):
            self.logger.info('path check success')
            self.start_download(self.get_info())
            return True
        else:
            self.logger.error('path check fail')
            return False

    @abstractmethod
    def get_info(self):
        pass

    def start_download(self, infos):
        for info in infos:
            attempt = 0
            while attempt < self.max_retry:
                if self.monitor_download(info):
                    self.logger.info(f'{info.id} download success')
                else:
                    attempt += 1
                    self.logger.info(f'{info.id} download timeout,{attempt} attempt')
            if attempt >= self.max_retry:
                self.logger.info(f'{info.id} download fail,skipping...')

    @abstractmethod
    def monitor_download(self, info):
        pass

    @abstractmethod
    def isExist(self, info, tar_dir):
        pass

    @staticmethod
    def start_popen(parameters, cwd):
        log_file = os.path.join(cwd, 'log', f'{time.strftime("%Y-%m-%d-bili", time.localtime())}.log')
        try:
            p = Popen(parameters, stdout=open(log_file, 'w'))
            p.wait(60 * 60)
            return True
        except TimeoutExpired:
            p.terminate()
            return False
