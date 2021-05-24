# -*- coding: utf-8 -*-#fv

# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2/22/2021 9:36 PM
import os
import time
import logging
from abc import ABCMeta, abstractmethod
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_abs(path):
    return path if os.path.isabs(path) else os.path.abspath(path)


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


def get_file_logger(level, name='foo'):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
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
    logger = get_file_logger(logging.DEBUG)
    folder = 'default'

    def __init__(self, download_script_repo, upper_repo, up):
        self.download_script_repo = download_script_repo
        self.repo = os.path.join(upper_repo, self.folder)
        self.up = up

    def main(self):
        self.logger.info(f'{self.folder} download start')
        if check_path(self.repo):
            self.logger.info('path check success')
            self.start_download(self.get_infos())
            return True
        else:
            self.logger.error('path check fail')
            return False

    def start_popen(self, parameters, cwd):
        log_file = os.path.join(cwd, 'log', f'{time.strftime("%Y-%m-%d-bili", time.localtime())}.log')
        Popen(parameters, stdout=open(log_file, 'w')).wait(60 * 60)

    @abstractmethod
    def get_infos(self):
        pass

    @abstractmethod
    def start_download(self, infos):
        pass
